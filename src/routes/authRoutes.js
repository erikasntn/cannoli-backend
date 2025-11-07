import express from "express";
import { register, login } from "../controllers/authController.js";
import { authenticateToken } from "../middlewares/authMiddleware.js";
import { findAllClients, findClientById } from "../repositories/userRepository.js";

const router = express.Router();

// Registro e login
router.post("/register", register);
router.post("/login", login);

// Exemplo: rota apenas para ADMIN visualizar todos os clientes
router.get("/clients", authenticateToken("admin"), async (req, res) => {
  const clients = await findAllClients();
  res.json(clients);
});

// Exemplo: rota para CLIENT visualizar apenas seus dados
router.get("/me", authenticateToken("client"), async (req, res) => {
  const client = await findClientById(req.user.id);
  res.json(client);
});

export default router;
