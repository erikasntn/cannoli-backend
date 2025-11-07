import { registerUser, loginUser } from "../services/authService.js";

export const register = async (req, res) => {
  try {
    console.log("📦 Dados recebidos:", req.body);
    const user = await registerUser(req.body);
    res.status(201).json({ message: "Usuário cadastrado com sucesso", user });
  } catch (err) {
    console.error("❌ Erro no registro:", err.message);
    res.status(400).json({ error: err.message });
  }
};


export const login = async (req, res) => {
  try {
    const data = await loginUser(req.body);
    res.json({
      message: "Login efetuado com sucesso",
      ...data,
    });
  } catch (err) {
    res.status(401).json({ error: err.message });
  }
};
