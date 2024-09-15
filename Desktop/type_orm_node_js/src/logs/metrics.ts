import express, { Request, Response, NextFunction } from 'express';
import prometheus from 'prom-client';

// Create a new express router for metrics
const metricsRouter = express.Router();
const register = new prometheus.Registry();

// Define metrics
const httpRequestDurationSeconds = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10] // Buckets for histogram
});

register.registerMetric(httpRequestDurationSeconds);

// Middleware to track request duration
metricsRouter.use((req: Request, res: Response, next: NextFunction) => {
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
metricsRouter.get('/metrics', async (req: Request, res: Response) => {
  res.setHeader('Content-Type', register.contentType);
  res.end(await register.metrics());
});

export default metricsRouter;
