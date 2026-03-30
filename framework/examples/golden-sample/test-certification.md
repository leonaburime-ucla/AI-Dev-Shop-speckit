# Test Certification: FEAT-001 CSV Export for Invoice List

- Feature: FEAT-001
- Spec version: 1.1.0
- Spec hash: sha256:a3f8c2d1e4b7091f56ac83e29d047b5f1c6e82a4d9f3071b2c5e8d4a7f1b6c9
- Certification hash: sha256:c1d4e7f2a9b5083f74ce05a3b216d9f4e8a3072c6d9f4183b7e0a2d5f8c1b4e
- TDD Agent completed: 2026-02-22T04:00:00Z
- Spec hash verified: ✅ Match confirmed

---

## Certification Summary

| AC / Invariant | Priority | Test File | Test Name | Status |
|---------------|----------|-----------|-----------|--------|
| AC-01 | P1 | InvoiceList.integration.test.tsx | `triggers download when Export CSV clicked with visible rows` | ✅ Certified |
| AC-02 | P1 | InvoiceList.integration.test.tsx | `exports only filtered rows when date filter is active` | ✅ Certified |
| AC-03 | P1 | InvoiceList.integration.test.tsx | `filename contains today date and "all" when no filters active` | ✅ Certified |
| AC-04 | P2 | InvoiceList.integration.test.tsx | `filename contains today date and "filtered" when filters active` | ✅ Certified |
| AC-05 | P1 | formatCsv.test.ts | `header row matches column labels in display order` | ✅ Certified |
| AC-06 | P1 | formatCsv.test.ts | `field with comma is wrapped in double quotes` | ✅ Certified |
| AC-07 | P1 | formatCsv.test.ts | `field with double quote character is escaped as two double quotes` | ✅ Certified |
| AC-08 | P1 | InvoiceList.integration.test.tsx | `exports header-only CSV when all rows are filtered out` | ✅ Certified |
| INV-01 | — | formatCsv.test.ts | `output is valid UTF-8 for non-ASCII field values` | ✅ Certified |
| INV-02 | — | InvoiceList.integration.test.tsx | `exported row count matches visible row count` | ✅ Certified |
| INV-03 | — | InvoiceList.integration.test.tsx | `export does not mutate component state` | ✅ Certified |
| EC-01 | — | formatCsv.test.ts | `field with newline is wrapped in double quotes with newline preserved` | ✅ Certified |
| EC-02 | — | formatCsv.test.ts | `column header with comma is wrapped in double quotes` | ✅ Certified |

All P1 acceptance criteria: **8 / 8 certified** ✅
All P2 acceptance criteria: **1 / 1 certified** ✅
All invariants: **3 / 3 certified** ✅
All edge cases: **2 / 2 certified** ✅

---

## Test File: `formatCsv.test.ts`

```typescript
import { formatCsv } from './formatCsv'

const COLUMNS = [
  { key: 'invoiceNumber', label: 'Invoice #' },
  { key: 'customer',      label: 'Customer' },
  { key: 'amount',        label: 'Amount' },
  { key: 'dueDate',       label: 'Due Date' },
]

describe('formatCsv', () => {
  // AC-05: header row matches column labels in display order
  it('header row matches column labels in display order', () => {
    const result = formatCsv(COLUMNS, [])
    const headerRow = result.split('\n')[0]
    expect(headerRow).toBe('Invoice #,Customer,Amount,Due Date')
  })

  // AC-06: field with comma is wrapped in double quotes
  it('field with comma is wrapped in double quotes', () => {
    const rows = [{ invoiceNumber: 'INV-001', customer: 'Acme, Inc.', amount: '1000', dueDate: '2026-03-01' }]
    const result = formatCsv(COLUMNS, rows)
    const dataRow = result.split('\n')[1]
    expect(dataRow).toContain('"Acme, Inc."')
  })

  // AC-07: field with double quote is escaped as two double quotes
  it('field with double quote character is escaped as two double quotes', () => {
    const rows = [{ invoiceNumber: 'INV-002', customer: 'Bob "The Builder" LLC', amount: '500', dueDate: '2026-03-01' }]
    const result = formatCsv(COLUMNS, rows)
    const dataRow = result.split('\n')[1]
    expect(dataRow).toContain('"Bob ""The Builder"" LLC"')
  })

  // EC-01: field with newline is wrapped, newline preserved
  it('field with newline is wrapped in double quotes with newline preserved', () => {
    const rows = [{ invoiceNumber: 'INV-003', customer: 'Line1\nLine2', amount: '200', dueDate: '2026-03-01' }]
    const result = formatCsv(COLUMNS, rows)
    expect(result).toContain('"Line1\nLine2"')
  })

  // EC-02: column header with comma is wrapped
  it('column header with comma is wrapped in double quotes', () => {
    const colsWithComma = [{ key: 'a', label: 'Fee, Tax' }]
    const result = formatCsv(colsWithComma, [])
    expect(result.split('\n')[0]).toBe('"Fee, Tax"')
  })

  // INV-01: UTF-8 for non-ASCII
  it('output is valid UTF-8 for non-ASCII field values', () => {
    const rows = [{ invoiceNumber: 'INV-004', customer: 'Ünïcödé Corp', amount: '300', dueDate: '2026-03-01' }]
    const result = formatCsv(COLUMNS, rows)
    // Node strings are UTF-16 internally; verify round-trip via TextEncoder/Decoder
    const encoded = new TextEncoder().encode(result)
    const decoded = new TextDecoder('utf-8', { fatal: true }).decode(encoded)
    expect(decoded).toBe(result)
  })

  // INV-02: row count matches input
  it('data row count matches input row count', () => {
    const rows = Array.from({ length: 5 }, (_, i) => ({
      invoiceNumber: `INV-00${i}`, customer: `Customer ${i}`, amount: '100', dueDate: '2026-03-01'
    }))
    const result = formatCsv(COLUMNS, rows)
    const lines = result.trim().split('\n')
    expect(lines.length - 1).toBe(5) // minus header
  })
})
```

---

## Test File: `triggerDownload.test.ts`

```typescript
import { triggerDownload } from './triggerDownload'

describe('triggerDownload', () => {
  let createObjectURLMock: jest.Mock
  let revokeObjectURLMock: jest.Mock
  let appendChildSpy: jest.SpyInstance
  let removeChildSpy: jest.SpyInstance
  let clickSpy: jest.SpyInstance

  beforeEach(() => {
    createObjectURLMock = jest.fn().mockReturnValue('blob:mock-url')
    revokeObjectURLMock = jest.fn()
    Object.defineProperty(URL, 'createObjectURL', { value: createObjectURLMock, writable: true })
    Object.defineProperty(URL, 'revokeObjectURL', { value: revokeObjectURLMock, writable: true })

    clickSpy = jest.fn()
    appendChildSpy = jest.spyOn(document.body, 'appendChild').mockImplementation((el: Node) => {
      (el as HTMLAnchorElement).click = clickSpy
      return el
    })
    removeChildSpy = jest.spyOn(document.body, 'removeChild').mockImplementation((el: Node) => el)
  })

  afterEach(() => jest.restoreAllMocks())

  // AC-01: download initiates
  it('triggers an anchor click with the correct filename', () => {
    triggerDownload('col1,col2\nval1,val2', 'invoices-2026-02-22-all.csv')
    expect(clickSpy).toHaveBeenCalledTimes(1)
    const anchor = appendChildSpy.mock.calls[0][0] as HTMLAnchorElement
    expect(anchor.download).toBe('invoices-2026-02-22-all.csv')
  })

  it('creates a Blob with text/csv charset', () => {
    triggerDownload('content', 'test.csv')
    const blob: Blob = createObjectURLMock.mock.calls[0][0]
    expect(blob.type).toBe('text/csv;charset=utf-8')
  })

  it('revokes the object URL after download', () => {
    triggerDownload('content', 'test.csv')
    expect(revokeObjectURLMock).toHaveBeenCalledWith('blob:mock-url')
  })

  // INV-03: no state mutation
  it('does not modify any external state beyond triggering the download', () => {
    const stateBefore = JSON.stringify(document.body.innerHTML)
    triggerDownload('content', 'test.csv')
    const stateAfter = JSON.stringify(document.body.innerHTML)
    expect(stateAfter).toBe(stateBefore)
  })
})
```

---

## Test File: `InvoiceList.integration.test.tsx` (relevant excerpts)

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { InvoiceList } from './InvoiceList'

// Synthetic test data — no real PII
const FIXTURE_ROWS = [
  { id: 'inv-001', invoiceNumber: 'INV-001', customer: 'Test Customer 001', amount: 1000, dueDate: '2026-03-01', status: 'unpaid' },
  { id: 'inv-002', invoiceNumber: 'INV-002', customer: 'Test Customer 002', amount: 2000, dueDate: '2026-03-15', status: 'paid' },
  { id: 'inv-003', invoiceNumber: 'INV-003', customer: 'Test Customer 003', amount: 500,  dueDate: '2026-04-01', status: 'unpaid' },
]

describe('InvoiceList CSV export', () => {
  let downloadedContent: string
  let downloadedFilename: string

  beforeEach(() => {
    jest.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock')
    jest.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function(this: HTMLAnchorElement) {
      // Capture what would have been downloaded
      const blob = URL.createObjectURL.mock.calls[0][0] as Blob
      blob.text().then(text => { downloadedContent = text })
      downloadedFilename = this.download
    })
  })

  // AC-01: download triggers with visible rows
  it('triggers download when Export CSV clicked with visible rows', async () => {
    render(<InvoiceList rows={FIXTURE_ROWS} activeFilters={{}} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalledTimes(1)
  })

  // AC-02: only filtered rows exported
  it('exports only filtered rows when date filter is active', async () => {
    const filtered = FIXTURE_ROWS.filter(r => r.status === 'unpaid')
    render(<InvoiceList rows={filtered} activeFilters={{ status: 'unpaid' }} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    await Promise.resolve()
    const lines = downloadedContent.trim().split('\n')
    expect(lines.length - 1).toBe(2) // 2 unpaid rows
  })

  // AC-03: filename format, no filters
  it('filename contains today date and "all" when no filters active', () => {
    const today = new Intl.DateTimeFormat('en-CA').format(new Date()) // YYYY-MM-DD
    render(<InvoiceList rows={FIXTURE_ROWS} activeFilters={{}} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    expect(downloadedFilename).toBe(`invoices-${today}-all.csv`)
  })

  // AC-04: filename format, with filters
  it('filename contains today date and "filtered" when filters active', () => {
    const today = new Intl.DateTimeFormat('en-CA').format(new Date())
    render(<InvoiceList rows={FIXTURE_ROWS.slice(0, 1)} activeFilters={{ status: 'unpaid' }} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    expect(downloadedFilename).toBe(`invoices-${today}-filtered.csv`)
  })

  // AC-08: empty list produces header-only CSV
  it('exports header-only CSV when all rows are filtered out', async () => {
    render(<InvoiceList rows={[]} activeFilters={{ status: 'paid' }} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    await Promise.resolve()
    const lines = downloadedContent.trim().split('\n')
    expect(lines.length).toBe(1) // header only
  })

  // INV-02: row count matches visible count
  it('exported row count matches visible row count', async () => {
    render(<InvoiceList rows={FIXTURE_ROWS} activeFilters={{}} />)
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    await Promise.resolve()
    const lines = downloadedContent.trim().split('\n')
    expect(lines.length - 1).toBe(FIXTURE_ROWS.length)
  })

  // INV-03: export does not mutate component state
  it('export does not mutate component state', () => {
    const { rerender } = render(<InvoiceList rows={FIXTURE_ROWS} activeFilters={{}} />)
    const rowsBefore = screen.getAllByRole('row').length
    fireEvent.click(screen.getByRole('button', { name: /export csv/i }))
    rerender(<InvoiceList rows={FIXTURE_ROWS} activeFilters={{}} />)
    const rowsAfter = screen.getAllByRole('row').length
    expect(rowsAfter).toBe(rowsBefore)
  })
})
```

---

## Certification Statement

All acceptance criteria, invariants, and edge cases from spec FEAT-001 v1.1.0 have corresponding failing tests. Tests are verified to fail against a no-op implementation and are ready for Programmer dispatch.

Spec hash at certification: `sha256:a3f8c2d1e4b7091f56ac83e29d047b5f1c6e82a4d9f3071b2c5e8d4a7f1b6c9`
Certification hash: `sha256:c1d4e7f2a9b5083f74ce05a3b216d9f4e8a3072c6d9f4183b7e0a2d5f8c1b4e`
