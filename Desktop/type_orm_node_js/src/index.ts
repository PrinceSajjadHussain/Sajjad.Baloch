import express, { Request, Response, NextFunction } from "express";
import bodyParser from "body-parser";
import cors from "cors";
import fs from "fs";
import https from "https";
import { connectDB } from "./middleware/dbMiddleware";
import userRequestRoutes from "./routes/userRequestRoutes";
import lovsRoutes from "./routes/lovsRoutes";
import fileRoutes from "./routes/fileRoutes";
import { constants } from "crypto";
import dotenv from "dotenv";
import { tidMiddleware } from "./middleware/tidMiddleware";
import metricsRouter from "./logs/metrics";
import { requestLogger } from "./middleware/requestLogger";
import { responseLogger } from "./middleware/responseLogger";
import { errorLogger } from "./middleware/errorLogger";
import { logger } from "./logs/logger";
import { methodFilter } from "./middleware/methodFilter";
import { notFoundHandler } from "./middleware/notFoundHandler";
import { sendToElasticsearch } from "./middleware/userRequestMiddleware";

// Define the paths to your SSL certificate and key files
const privateKeyPath = './key.pem';
const certificatePath = './cert.pem';

// Load SSL certificates
const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
const certificate = fs.readFileSync(certificatePath, 'utf8');

dotenv.config();

const app = express();

// Configure body parser to accept large payloads
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));
app.use('/assets', express.static('product'));

app.use(cors());
const apiMetrics = require("prometheus-api-metrics");
app.use(apiMetrics());

app.use(connectDB);
// app.use(sendToElasticsearch)
app.use(tidMiddleware);

app.use(methodFilter(logger));

// Add the new endpoint that uses the userRequestLogger middleware
app.post('/generate-user-request', async (req: Request, res: Response) => {
  // const users = await getUserRequestsService();

  await sendToElasticsearch()
  res.status(200).json({ message: "Success" });
});


// Use request and response loggers as middleware
app.use(requestLogger(logger));
app.use(responseLogger(logger));

app.use("/api", userRequestRoutes);  // Prefix all routes with /api
app.use("/api", fileRoutes);  // Add the file routes
app.use("/api", lovsRoutes);  // Add the LOVs routes

// 404 Error handling middleware
app.use(notFoundHandler(logger));

// Error logging middleware
app.use(errorLogger(logger));

// Create HTTPS server with TLS options
const httpsServer = https.createServer({
  key: privateKey,
  cert: certificate,
  secureOptions: constants.SSL_OP_NO_TLSv1 | constants.SSL_OP_NO_TLSv1_1
}, app);

httpsServer.listen(3005, async () => {
  console.log("HTTPS Server is running on port 3005");
});