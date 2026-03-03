# Orc-BASH TypeDoc + Return Types Example

This reference shows a minimal, end-to-end Orc-BASH slice with:

- Explicit return types in function signatures
- TypeDoc/TSDoc on exported APIs and hooks
- TypeDoc/TSDoc on internal hooks with non-trivial behavior

## `types/post.ts`

```typescript
export interface Post {
  id: string;
  title: string;
  content: string;
  likes: number;
  commentCount: number;
}

export interface FormattedPost extends Post {
  excerpt: string;
  engagementScore: number;
}
```

## `hooks/usePost.ts`

```typescript
import { useCallback, useMemo, useState } from 'react';
import type { FormattedPost, Post } from '../types/post';

export interface UsePostDependencies {
  post: Post | null;
  fetchPost: ({ postId }: { postId: string }, optional?: { signal?: AbortSignal }) => Promise<Post>;
  likePost: ({ postId }: { postId: string }) => Promise<{ likes: number }>;
  formatPost: ({ post }: { post: Post }) => FormattedPost;
  savePost: (post: Post) => void;
  updatePostLikes: ({ postId, likes }: { postId: string; likes: number }) => void;
}

interface PostUiState {
  isLiking: boolean;
}

interface UsePostUiStateResult {
  uiState: PostUiState;
  actions: {
    setLiking: (v: boolean) => void;
  };
}

interface UsePostLogicResult {
  formattedPost: FormattedPost | null;
}

export interface UsePostResult {
  post: FormattedPost | null;
  isLoading: boolean;
  error: Error | null;
  uiState: PostUiState;
  actions: {
    fetchPost: () => Promise<void>;
    like: () => Promise<void>;
  };
}

/**
 * Manages ephemeral UI-only state used by the integration hook.
 * @returns UI state snapshot and mutator actions.
 */
const usePostUiState = (): UsePostUiStateResult => {
  const [uiState, setUiState] = useState<PostUiState>({ isLiking: false });
  const setLiking = useCallback((v: boolean): void => {
    setUiState({ isLiking: v });
  }, []);
  return { uiState, actions: { setLiking } };
};

/**
 * Computes memoized, domain-derived post view data.
 * @param post Current post entity from state.
 * @param formatPost Domain formatter function.
 * @returns Formatted post view model for UI consumption.
 */
const usePostLogic = ({
  post,
  formatPost,
}: {
  post: Post | null;
  formatPost: ({ post }: { post: Post }) => FormattedPost;
}): UsePostLogicResult => {
  const formattedPost = useMemo(
    (): FormattedPost | null => (post ? formatPost({ post }) : null),
    [post, formatPost],
  );
  return { formattedPost };
};

/**
 * Composes UI state, business logic, and async integration concerns.
 * @param postId Target post identifier.
 * @param deps Injected dependencies from orchestrator wiring.
 * @returns Orchestrated state and actions for post views.
 */
export const usePost = (
  { postId, deps }: { postId: string; deps: UsePostDependencies },
  { prefetchOnInit = false }: { prefetchOnInit?: boolean } = {},
): UsePostResult => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const ui = usePostUiState();
  const logic = usePostLogic({
    post: deps.post,
    formatPost: deps.formatPost,
  });

  const fetchPost = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const fetched = await deps.fetchPost({ postId });
      deps.savePost(fetched);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [postId, deps]);

  const like = useCallback(async (): Promise<void> => {
    ui.actions.setLiking(true);
    try {
      const { likes } = await deps.likePost({ postId });
      deps.updatePostLikes({ postId, likes });
    } catch (err) {
      setError(err as Error);
    } finally {
      ui.actions.setLiking(false);
    }
  }, [postId, deps, ui.actions]);

  return {
    post: logic.formattedPost,
    isLoading,
    error,
    uiState: ui.uiState,
    actions: { fetchPost, like },
  };
};
```

## `orchestrators/PostPageOrchestrator.ts`

```typescript
import * as postApi from '../api/postApi';
import { postService } from '../logic/PostService';
import { usePostStateAdapter } from '../state/PostStateAdapter';
import { usePost, type UsePostResult } from '../hooks/usePost';
import type { FormattedPost } from '../types/post';

export interface UsePostPageOrchestratorResult {
  post: FormattedPost | null;
  isLoading: boolean;
  error: Error | null;
  isLiking: boolean;
  onLike: () => Promise<void>;
}

/**
 * Wires all Orc-BASH dependencies for the post page use case.
 * @param postId Target post identifier.
 * @returns UI-ready view model and actions.
 */
export const usePostPageOrchestrator = (
  { postId }: { postId: string },
): UsePostPageOrchestratorResult => {
  const state = usePostStateAdapter({ postId });
  const hook: UsePostResult = usePost({ postId, deps: {
    post: state.post,
    fetchPost: postApi.fetchPost,
    likePost: postApi.likePost,
    formatPost: postService.formatPost.bind(postService),
    savePost: state.savePost,
    updatePostLikes: state.updatePostLikes,
  } });

  return {
    post: hook.post,
    isLoading: hook.isLoading,
    error: hook.error,
    isLiking: hook.uiState.isLiking,
    onLike: hook.actions.like,
  };
};
```

## Notes

- Keep examples realistic but concise; this file is a pattern reference, not a production template.
- If internal hooks are trivial one-liners with no behavior, TypeDoc is optional; if they coordinate state/effects/domain behavior, TypeDoc is required.
