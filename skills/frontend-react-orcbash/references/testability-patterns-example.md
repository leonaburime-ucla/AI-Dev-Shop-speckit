# Orc-BASH Testability Patterns (Functions, Hooks, Orchestrators)

This reference is a general guide for writing code that is easy to test across all Orc-BASH layers.

## 1) Pure Logic Function Pattern

```typescript
export interface SelectModelInput {
  availableModels: string[];
  preferredModel: string | null;
}

export interface SelectModelResult {
  selectedModel: string;
  fallbackUsed: boolean;
}

/**
 * Selects a model deterministically from available options.
 * @param input Model-selection inputs.
 * @returns Selected model and whether fallback logic was used.
 */
export const selectModel = (
  { availableModels, preferredModel }: SelectModelInput,
  {}: {} = {},
): SelectModelResult => {
  if (preferredModel && availableModels.includes(preferredModel)) {
    return { selectedModel: preferredModel, fallbackUsed: false };
  }
  return {
    selectedModel: availableModels[0] ?? 'default-model',
    fallbackUsed: true,
  };
};
```

Why this is testable:
- explicit typed input/output
- deterministic return value
- no hidden dependencies

## 2) API Function Pattern (Injectable Boundary)

```typescript
export interface HttpClient {
  post: (
    { url, body }: { url: string; body: unknown },
    optional?: { signal?: AbortSignal },
  ) => Promise<{ ok: boolean; json: () => Promise<unknown> }>;
}

export interface SendMessageInput {
  message: string;
  model: string;
}

export interface SendMessageOutput {
  reply: string;
}

/**
 * Sends a message request through an injected HTTP client.
 * @param http Injected HTTP boundary.
 * @param input Request payload.
 * @returns Parsed reply payload.
 */
export const sendMessage = async (
  { http, input }: { http: HttpClient; input: SendMessageInput },
  { signal }: { signal?: AbortSignal } = {},
): Promise<SendMessageOutput> => {
  const response = await http.post({ url: '/api/chat', body: input }, { signal });
  if (!response.ok) throw new Error('CHAT_REQUEST_FAILED');
  const body = (await response.json()) as { reply: string };
  return { reply: body.reply };
};
```

Why this is testable:
- transport boundary injected
- behavior asserted via output/throw paths
- no framework coupling

## 3) Hook Pattern (Assertion-Friendly Contract)

```typescript
import { useCallback, useState } from 'react';

export interface UseChatDeps {
  sendMessage: (
    { input }: { input: { message: string; model: string } },
    optional?: { signal?: AbortSignal },
  ) => Promise<{ reply: string }>;
}

export interface UseChatState {
  isSending: boolean;
  error: Error | null;
  reply: string | null;
}

export interface UseChatActions {
  submit: ({ message, model }: { message: string; model: string }, optional?: { signal?: AbortSignal }) => Promise<void>;
  reset: () => void;
}

export interface UseChatResult {
  state: UseChatState;
  actions: UseChatActions;
}

/**
 * Coordinates chat submission and exposes test-friendly state/actions.
 * @param deps Injected dependencies.
 * @returns Stable state/action contract for UI and tests.
 */
export const useChat = (
  { deps }: { deps: UseChatDeps },
  {}: {} = {},
): UseChatResult => {
  const [state, setState] = useState<UseChatState>({
    isSending: false,
    error: null,
    reply: null,
  });

  const submit = useCallback(async (
    { message, model }: { message: string; model: string },
    { signal }: { signal?: AbortSignal } = {},
  ): Promise<void> => {
    setState((s) => ({ ...s, isSending: true, error: null }));
    try {
      const result = await deps.sendMessage({ input: { message, model } }, { signal });
      setState({ isSending: false, error: null, reply: result.reply });
    } catch (err) {
      setState((s) => ({ ...s, isSending: false, error: err as Error }));
    }
  }, [deps]);

  const reset = useCallback((): void => {
    setState({ isSending: false, error: null, reply: null });
  }, []);

  return { state, actions: { submit, reset } };
};
```

Why this is testable:
- explicit state/action return contract
- assertions target observable state transitions
- async action contract is explicit (`Promise<void>`)

## 4) Orchestrator Pattern (Thin Wiring Only)

```typescript
import { useChat } from '../hooks/useChat';
import * as chatApi from '../api/chatApi';

export interface UseChatPageOrchestratorResult {
  state: {
    isSending: boolean;
    error: Error | null;
    reply: string | null;
  };
  actions: {
    submit: ({ message, model }: { message: string; model: string }, optional?: { signal?: AbortSignal }) => Promise<void>;
    reset: () => void;
  };
}

/**
 * Wires runtime dependencies to the chat hook.
 * @returns UI-ready chat state/actions.
 */
export const useChatPageOrchestrator = (): UseChatPageOrchestratorResult => {
  return useChat({ deps: { sendMessage: chatApi.sendMessage } });
};
```

Why this is testable:
- orchestrator is thin wiring, easy to integration-test
- core behavior remains in hook/logic layers

## 5) Practical Test Mapping

- `logic/*.ts` -> unit tests in `__tests__/unit/*.unit.test.ts`
- `api/*.ts` boundary behavior -> integration tests in `__tests__/integration/*.integration.test.ts`
- `hooks/*.ts` state/action contract -> unit or integration tests (depending on boundaries)
- `orchestrators/*.ts` wiring correctness -> integration tests in `__tests__/integration/*.integration.test.ts`
- user journeys -> E2E tests in `__tests__/e2e/*.e2e.test.ts`

## 6) Design Smells (Refactor Immediately)

- Function has hidden globals/time/random/network calls.
- Hook returns ambiguous nested data with no stable action interface.
- Orchestrator contains domain logic instead of dependency wiring.
- Tests require mocking too many unrelated dependencies.
- You can only verify behavior by checking internals instead of outputs/state transitions.
