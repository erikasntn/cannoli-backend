import express from "express";
import { getDashboardAdmin, getDashboardClient } from "../controllers/dashboardController.js";
import { authenticateToken } from "../utils/jwt.js";

const router = express.Router();

router.get("/admin", authenticateToken("admin"), getDashboardAdmin);
router.get("/client", authenticateToken("client"), getDashboardClient);

export default router;
