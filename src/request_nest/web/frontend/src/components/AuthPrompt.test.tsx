import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthPrompt } from "./AuthPrompt";
import { getToken } from "../utils";
import { renderWithProviders } from "../test/utils";

describe("AuthPrompt", () => {
  it("renders auth prompt dialog", () => {
    renderWithProviders(<AuthPrompt onAuthenticated={vi.fn()} />);

    expect(screen.getByText("auth required")).toBeInTheDocument();
    expect(screen.getByLabelText(/token/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /authenticate/i }),
    ).toBeInTheDocument();
  });

  it("stores token when form is submitted", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    renderWithProviders(<AuthPrompt onAuthenticated={onAuthenticated} />);

    await user.type(screen.getByLabelText(/token/i), "test-token-123");
    await user.click(screen.getByRole("button", { name: /authenticate/i }));

    expect(getToken()).toBe("test-token-123");
  });

  it("calls onAuthenticated after token is stored", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    renderWithProviders(<AuthPrompt onAuthenticated={onAuthenticated} />);

    await user.type(screen.getByLabelText(/token/i), "my-token");
    await user.click(screen.getByRole("button", { name: /authenticate/i }));

    expect(onAuthenticated).toHaveBeenCalledTimes(1);
  });

  it("shows error when submitting empty token", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    renderWithProviders(<AuthPrompt onAuthenticated={onAuthenticated} />);

    await user.click(screen.getByRole("button", { name: /authenticate/i }));

    expect(
      screen.getByText(/please enter your admin token/i),
    ).toBeInTheDocument();
    expect(onAuthenticated).not.toHaveBeenCalled();
  });

  it("trims whitespace from token", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    renderWithProviders(<AuthPrompt onAuthenticated={onAuthenticated} />);

    await user.type(screen.getByLabelText(/token/i), "  spaced-token  ");
    await user.click(screen.getByRole("button", { name: /authenticate/i }));

    expect(getToken()).toBe("spaced-token");
  });
});
