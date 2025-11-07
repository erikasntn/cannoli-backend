import { createUser, findUserByEmail } from "../repositories/userRepository.js";
import { hashPassword, comparePassword } from "../utils/hash.js";
import jwt from "jsonwebtoken";
import dotenv from "dotenv";

dotenv.config();

export const registerUser = async (userData) => {
  const existingUser = await findUserByEmail(userData.email);
  if (existingUser) throw new Error("Usuário já existe");

  userData.password = await hashPassword(userData.password);
  const user = await createUser(userData);
  return user;
};

export const loginUser = async (userData) => {
  const user = await findUserByEmail(userData.email);
  if (!user) throw new Error("Usuário não encontrado");

  const valid = await comparePassword(userData.password, user.password);
  if (!valid) throw new Error("Senha inválida");

  const token = jwt.sign(
    { id: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "1d" }
  );

  return {
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
      storeName: user.storeName,
    },
    token,
  };
};
