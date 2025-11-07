import { Sequelize } from "sequelize";
import dotenv from "dotenv";

dotenv.config();
console.log("DB_USER =", process.env.DB_USER);

const sequelize = new Sequelize(
  process.env.DB_NAME,
  process.env.DB_USER,
  process.env.DB_PASS,
  {
    host: process.env.DB_HOST,
    port: 3306,
    dialect: "mysql",
    logging: false, // opcional, evita logs enormes
  }
);

sequelize
  .authenticate()
  .then(() => {
    console.log("✅ Conexão com o banco de dados estabelecida com sucesso.");
  })
  .catch((error) => {
    console.error("❌ Não foi possível conectar ao banco de dados:", error);
  });

export default sequelize;
