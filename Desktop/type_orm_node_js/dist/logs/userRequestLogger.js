"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.esTransportOptions = exports.esClient = exports.userRequestLogger = void 0;
const winston_1 = __importStar(require("winston"));
const winston_elasticsearch_1 = require("winston-elasticsearch");
const elasticsearch_1 = require("@elastic/elasticsearch");
// Configure Elasticsearch client
const esClient = new elasticsearch_1.Client({ node: 'http://localhost:9200' });
exports.esClient = esClient;
// Configure Elasticsearch transport for Winston
const esTransportOptions = {
    level: 'info',
    client: esClient,
    indexPrefix: 'user-request-logs',
    format: winston_1.format.json(),
};
exports.esTransportOptions = esTransportOptions;
const esTransport = new winston_elasticsearch_1.ElasticsearchTransport(esTransportOptions);
const userRequestLogger = winston_1.default.createLogger({
    level: 'info',
    format: winston_1.format.combine(winston_1.format.timestamp(), winston_1.format.json()),
    transports: [
        esTransport
    ]
});
exports.userRequestLogger = userRequestLogger;
