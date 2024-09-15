"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestLogger = void 0;
/**
 * Creates a middleware function that logs incoming HTTP requests.
 *
 * This middleware logs details about each request, including the HTTP method, URL,
 * IP address, user agent, transaction ID (TID), and a modified version of the request body.
 * The modified request body includes placeholder values for certain properties if they are present.
 *
 * @param logger - A winston logger instance used for logging request details.
 * @returns An Express middleware function.
 */
const requestLogger = (logger) => {
    return (req, res, next) => {
        var _a;
        // Modify the request body based on specific properties
        const body = ((_a = req === null || req === void 0 ? void 0 : req.body) === null || _a === void 0 ? void 0 : _a.hasOwnProperty("base64")) ? Object.assign(Object.assign({}, req === null || req === void 0 ? void 0 : req.body), { base64: "base64" }) :
            req.body.hasOwnProperty("liveImage") ? Object.assign(Object.assign({}, req.body), { liveImage: "base64" }) :
                req.body.hasOwnProperty("accountType") ? Object.assign(Object.assign({}, req === null || req === void 0 ? void 0 : req.body), { cnicFront: "base64", cnicBack: "base64" }) :
                    req.body;
        // Create a log entry object with request details
        const logEntry = {
            timestamp: new Date().toISOString(),
            method: req.method,
            url: req.originalUrl,
            ip: req.ip,
            userAgent: req.get('User-Agent') || '',
            tid: req.headers.tid,
            logMessage: JSON.stringify(body), // Log the modified request body
            type: 'req',
            status: "", // Status will be set in the response logging, if needed
        };
        // Log the request details using the provided logger
        logger.info(logEntry);
        // Pass control to the next middleware or route handler
        next();
    };
};
exports.requestLogger = requestLogger;
