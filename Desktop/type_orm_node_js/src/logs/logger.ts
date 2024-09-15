import winston, { format, Logger } from 'winston';
import { ElasticsearchTransportOptions, ElasticsearchTransport } from 'winston-elasticsearch';
import { Client } from '@elastic/elasticsearch';

// Configure Elasticsearch client
const esClient = new Client({ node: 'http://localhost:9200' });

// Configure Elasticsearch transport for Winston
const esTransportOptions: ElasticsearchTransportOptions = {
  level: 'info',
  client: esClient,
  indexPrefix: 'api-logs',
  format: format.json(),
};

const esTransport = new ElasticsearchTransport(esTransportOptions);

const logger: Logger = winston.createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    esTransport
  ]
});

export { logger, esClient, esTransportOptions };