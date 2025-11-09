import { Sequelize } from "sequelize";
import dotenv from "dotenv";

dotenv.config();

console.log("🌐 Conectando ao banco...");
console.log("HOST:", process.env.MYSQLHOST);

const sequelize = new Sequelize(
  process.env.MYSQLDATABASE,
  process.env.MYSQLUSER,
  process.env.MYSQLPASSWORD,
  {
    host: process.env.MYSQLHOST,
    port: process.env.MYSQLPORT,
    dialect: "mysql",
    dialectOptions: {
      ssl: {
        require: true,
        rejectUnauthorized: false,
      },
      connectTimeout: 60000,
    },
    pool: {
      max: 5,
      min: 0,
      acquire: 60000,
      idle: 10000,
    },
    logging: false,
  }
);

sequelize
  .authenticate()
  .then(() => console.log("✅ Conectado ao MySQL no Railway com sucesso!"))
  .catch((err) => console.error("❌ Erro na conexão:", err.message));

export default sequelize;
