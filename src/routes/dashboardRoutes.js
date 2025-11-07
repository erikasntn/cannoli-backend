import express from "express";
import { authenticateToken } from "../middlewares/authMiddleware.js";
import {
  handleInsights,
  handleAlerts,
  handleExport,
} from "../controllers/dashboardController.js";

const router = express.Router();

router.get("/insights/:period", authenticateToken(), handleInsights);
router.get("/alerts/:period", authenticateToken(), handleAlerts);
router.get("/export", authenticateToken(), handleExport);

export default router;
