"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const cors_1 = __importDefault(require("cors"));
const fs_1 = __importDefault(require("fs"));
const https_1 = __importDefault(require("https"));
const dbMiddleware_1 = require("./middleware/dbMiddleware");
const userRequestRoutes_1 = __importDefault(require("./routes/userRequestRoutes"));
const lovsRoutes_1 = __importDefault(require("./routes/lovsRoutes"));
const fileRoutes_1 = __importDefault(require("./routes/fileRoutes"));
const crypto_1 = require("crypto");
const dotenv_1 = __importDefault(require("dotenv"));
const tidMiddleware_1 = require("./middleware/tidMiddleware");
const requestLogger_1 = require("./middleware/requestLogger");
const responseLogger_1 = require("./middleware/responseLogger");
const errorLogger_1 = require("./middleware/errorLogger");
const logger_1 = require("./logs/logger");
const methodFilter_1 = require("./middleware/methodFilter");
const notFoundHandler_1 = require("./middleware/notFoundHandler");
const userRequestMiddleware_1 = require("./middleware/userRequestMiddleware");
// Define the paths to your SSL certificate and key files
const privateKeyPath = './key.pem';
const certificatePath = './cert.pem';
// Load SSL certificates
const privateKey = fs_1.default.readFileSync(privateKeyPath, 'utf8');
const certificate = fs_1.default.readFileSync(certificatePath, 'utf8');
dotenv_1.default.config();
const app = (0, express_1.default)();
// Configure body parser to accept large payloads
app.use(body_parser_1.default.json({ limit: '50mb' }));
app.use(body_parser_1.default.urlencoded({ limit: '50mb', extended: true }));
app.use('/assets', express_1.default.static('product'));
app.use((0, cors_1.default)());
const apiMetrics = require("prometheus-api-metrics");
app.use(apiMetrics());
app.use(dbMiddleware_1.connectDB);
// app.use(sendToElasticsearch)
app.use(tidMiddleware_1.tidMiddleware);
app.use((0, methodFilter_1.methodFilter)(logger_1.logger));
// Add the new endpoint that uses the userRequestLogger middleware
app.post('/generate-user-request', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    // const users = await getUserRequestsService();
    yield (0, userRequestMiddleware_1.sendToElasticsearch)();
    res.status(200).json({ message: "Success" });
}));
// Use request and response loggers as middleware
app.use((0, requestLogger_1.requestLogger)(logger_1.logger));
app.use((0, responseLogger_1.responseLogger)(logger_1.logger));
app.use("/api", userRequestRoutes_1.default); // Prefix all routes with /api
app.use("/api", fileRoutes_1.default); // Add the file routes
app.use("/api", lovsRoutes_1.default); // Add the LOVs routes
// 404 Error handling middleware
app.use((0, notFoundHandler_1.notFoundHandler)(logger_1.logger));
// Error logging middleware
app.use((0, errorLogger_1.errorLogger)(logger_1.logger));
// Create HTTPS server with TLS options
const httpsServer = https_1.default.createServer({
    key: privateKey,
    cert: certificate,
    secureOptions: crypto_1.constants.SSL_OP_NO_TLSv1 | crypto_1.constants.SSL_OP_NO_TLSv1_1
}, app);
httpsServer.listen(3005, () => __awaiter(void 0, void 0, void 0, function* () {
    console.log("HTTPS Server is running on port 3005");
}));
