import winston, { format, Logger } from 'winston';
import { ElasticsearchTransportOptions, ElasticsearchTransport } from 'winston-elasticsearch';
import { Client } from '@elastic/elasticsearch';

// Configure Elasticsearch client
const esClient = new Client({ node: 'http://localhost:9200' });

// Configure Elasticsearch transport for Winston
const esTransportOptions: ElasticsearchTransportOptions = {
  level: 'info',
  client: esClient,
  indexPrefix: 'user-request-logs',
  format: format.json(),
};

const esTransport = new ElasticsearchTransport(esTransportOptions);

const userRequestLogger: Logger = winston.createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    esTransport
  ]
});

export { userRequestLogger, esClient, esTransportOptions };