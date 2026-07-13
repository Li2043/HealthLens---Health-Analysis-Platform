import { beforeEach, describe, expect, it, vi } from "vitest";
import { readStoredMode, STORAGE_KEY } from "./analysisModeStorage";

function createStorage(initial: Record<string, string> = {}): Storage {
  const store = new Map(Object.entries(initial));

  return {
    get length() {
      return store.size;
    },
    clear() {
      store.clear();
    },
    getItem(key: string) {
      return store.has(key) ? store.get(key)! : null;
    },
    key(index: number) {
      return Array.from(store.keys())[index] ?? null;
    },
    removeItem(key: string) {
      store.delete(key);
    },
    setItem(key: string, value: string) {
      store.set(key, value);
    },
  };
}

describe("readStoredMode", () => {
  let storage: Storage;

  beforeEach(() => {
    storage = createStorage();
    vi.restoreAllMocks();
  });

  it("returns deepseek when localStorage is empty", () => {
    expect(readStoredMode(storage)).toBe("deepseek");
  });

  it("returns deepseek when stored value is deepseek", () => {
    storage.setItem(STORAGE_KEY, "deepseek");
    expect(readStoredMode(storage)).toBe("deepseek");
  });

  it("returns openai when stored value is openai", () => {
    storage.setItem(STORAGE_KEY, "openai");
    expect(readStoredMode(storage)).toBe("openai");
  });

  it("returns mock when stored value is mock", () => {
    storage.setItem(STORAGE_KEY, "mock");
    expect(readStoredMode(storage)).toBe("mock");
  });

  it("migrates ai to deepseek and persists the new value", () => {
    storage.setItem(STORAGE_KEY, "ai");

    expect(readStoredMode(storage)).toBe("deepseek");
    expect(storage.getItem(STORAGE_KEY)).toBe("deepseek");
  });

  it("returns deepseek for invalid stored values", () => {
    storage.setItem(STORAGE_KEY, "invalid-mode");
    expect(readStoredMode(storage)).toBe("deepseek");
  });
});
