import User from "../models/user.js";

// Cria novo usuário
export const createUser = async (userData) => await User.create(userData);

// Busca usuário por e-mail (login)
export const findUserByEmail = async (email) =>
  await User.findOne({ where: { email } });

// 🔹 Lista todos os clientes (para ADMIN)
export const findAllClients = async () =>
  await User.findAll({ where: { role: "client" } });

// 🔹 Busca um cliente pelo ID (para CLIENT)
export const findClientById = async (id) =>
  await User.findByPk(id);
