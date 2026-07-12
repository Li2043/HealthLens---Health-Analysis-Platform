export type AuthResponse = {
  token: string;
  email: string;
  userId: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
};

export type AuthUser = {
  email: string;
  userId: string;
};
