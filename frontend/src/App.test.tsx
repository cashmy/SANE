import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders the Stage 1 workflow placeholder", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: /inbound email governance, narrowed to the first loop/i,
      }),
    ).toBeInTheDocument();
    expect(screen.getByText("Connect")).toBeInTheDocument();
    expect(screen.getByText("Review Candidates")).toBeInTheDocument();
    expect(screen.getByText("Decide")).toBeInTheDocument();
    expect(screen.getByText("Complete")).toBeInTheDocument();
  });
});
