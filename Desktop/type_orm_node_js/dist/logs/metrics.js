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
const prom_client_1 = __importDefault(require("prom-client"));
// Create a new express router for metrics
const metricsRouter = express_1.default.Router();
const register = new prom_client_1.default.Registry();
// Define metrics
const httpRequestDurationSeconds = new prom_client_1.default.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.5, 1, 2.5, 5, 10] // Buckets for histogram
});
register.registerMetric(httpRequestDurationSeconds);
// Middleware to track request duration
metricsRouter.use((req, res, next) => {
    const end = httpRequestDurationSeconds.startTimer({
        method: req.method,
        route: req.route ? req.route.path : 'unknown'
    });
    res.on('finish', () => {
        end({ status_code: res.statusCode.toString() });
    });
    next();
});
// Metrics endpoint
metricsRouter.get('/metrics', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    res.setHeader('Content-Type', register.contentType);
    res.end(yield register.metrics());
}));
exports.default = metricsRouter;
