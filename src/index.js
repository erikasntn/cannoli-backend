import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import authRoutes from "./routes/authRoutes.js";
import dashboardRoutes from "./routes/dashboardRoutes.js";
import sequelize from "./config/database.js";
import { authenticateToken } from "./middlewares/authMiddleware.js";

dotenv.config();

const app = express();

// Configuração de CORS com JWT
app.use(cors({
  origin: [
    "https://erikasntn.github.io",           // GitHub Pages
    "https://erikasntn.github.io/cannoli-dashboard", // caminho completo se o projeto estiver em subpasta
  ],
  methods: ["GET", "POST", "PUT", "DELETE"],
  credentials: true,
}));

// Configuração de body parser + UTF-8
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use((req, res, next) => {
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  next();
});

// Rotas públicas (login e cadastro)
app.use("/api/auth", authRoutes);

// Rotas protegidas (dashboard só com token)
app.use("/api/dashboard", authenticateToken(), dashboardRoutes);

const PORT = process.env.PORT || 3000;

sequelize.sync({ alter: true }).then(() => {
  app.listen(PORT, () => console.log(`🚀 Servidor rodando na porta ${PORT}`));
});
