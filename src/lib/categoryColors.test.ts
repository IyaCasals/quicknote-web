import { describe, expect, it } from "vitest";

import { getCategoryColor } from "./categoryColors";

describe("getCategoryColor", () => {
  it("returns stable colors for the same seed", () => {
    expect(getCategoryColor("School")).toEqual(getCategoryColor("School"));
  });

  it("handles missing categories", () => {
    expect(getCategoryColor(null).text).toBeTruthy();
  });
});
