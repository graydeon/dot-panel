// SPDX-License-Identifier: AGPL-3.0-only
export const env={get DB(){return (globalThis as any).__testDB;}};
