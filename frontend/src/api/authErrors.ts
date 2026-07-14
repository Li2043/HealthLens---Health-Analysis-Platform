import { isAxiosError } from "axios";

type AuthErrorCopy = {
  failed: string;
  networkError: string;
  serverUnavailable: string;
};

export function getAuthErrorMessage(
  error: unknown,
  copy: AuthErrorCopy,
): string {
  if (!isAxiosError(error)) {
    return copy.failed;
  }

  const message = error.response?.data?.message;
  if (typeof message === "string" && message.length > 0) {
    return message;
  }

  if (!error.response) {
    if (error.code === "ECONNABORTED") {
      return copy.serverUnavailable;
    }
    return copy.networkError;
  }

  return copy.failed;
}
