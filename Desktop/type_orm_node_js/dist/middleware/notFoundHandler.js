"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.notFoundHandler = void 0;
/**
 * Creates a middleware function to handle 404 errors for undefined routes.
 *
 * This middleware is used to capture requests that do not match any defined routes and
 * respond with a custom 404 error message. It also logs detailed information about the
 * request and the error using the provided `winston` logger instance.
 *
 * @param logger - A winston logger instance used for logging 404 errors.
 * @returns An Express middleware function that handles 404 errors.
 */
const notFoundHandler = (logger) => {
    return (req, res, next) => {
        // Create a log entry object with request and error details
        const logEntry = {
            timestamp: new Date().toISOString(),
            method: req.method,
            url: req.originalUrl,
            ip: req.ip,
            userAgent: req.get('User-Agent') || '',
            tid: req.headers.tid || 'N/A', // Use 'N/A' if TID is not present
            logMessage: `Route ${req.originalUrl} not found`,
            status: 404, // HTTP status code for not found
        };
        // Log the 404 error using the provided logger
        logger.warn(logEntry);
        // Respond with a 404 status code and a JSON error message
        res.status(404).json({ error: 'Not Found', message: `Route ${req.originalUrl} not found` });
    };
};
exports.notFoundHandler = notFoundHandler;
