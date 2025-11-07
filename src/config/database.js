import { Sequelize } from "sequelize";
import dotenv from "dotenv";

dotenv.config();
console.log("DB_USER =", process.env.MYSQLUSER);

const sequelize = new Sequelize(
  process.env.MYSQLDATABASE,
  process.env.MYSQLUSER,
  process.env.MYSQLPASSWORD,
  {
    host: process.env.MYSQLHOST,
    port: MYSQLPORT,
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
