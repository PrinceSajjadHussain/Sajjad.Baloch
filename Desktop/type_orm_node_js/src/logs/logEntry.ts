class LogEntry {
  timestamp: string;
  tid: string;
  level: string;
  url: string;
  urlMethod: string;
  httpStatus: number;
  requestMessage: string;
  responseMessage: string;

  constructor(
    tid: string,
    level: string,
    url: string,
    urlMethod: string,
    httpStatus: number,
    requestMessage: string,
    responseMessage: string
  ) {
    this.timestamp = new Date().toISOString(); // Automatically set the timestamp to the current date and time in ISO format
    this.tid = tid;                             // Unique transaction ID
    this.level = level;                         // Log level (e.g., 'info', 'error', etc.)
    this.url = url;                             // Request URL
    this.urlMethod = urlMethod;                 // HTTP method (e.g., 'GET', 'POST')
    this.httpStatus = httpStatus;               // HTTP status code (e.g., 200, 404)
    this.requestMessage = requestMessage;       // Request message content
    this.responseMessage = responseMessage;     // Response message content
  }

  // Method to convert the log entry to JSON format
  toJSON(): string {
    return JSON.stringify({
      timestamp: this.timestamp,
      tid: this.tid,
      level: this.level,
      url: this.url,
      urlMethod: this.urlMethod,
      httpStatus: this.httpStatus,
      requestMessage: this.requestMessage,
      responseMessage: this.responseMessage
    });
  }

  // Static method to create a LogEntry from an object (e.g., when deserializing from JSON)
  static fromObject(obj: {
    tid: string;
    level: string;
    url: string;
    urlMethod: string;
    httpStatus: number;
    requestMessage: string;
    responseMessage: string;
  }): LogEntry {
    return new LogEntry(
      obj.tid,
      obj.level,
      obj.url,
      obj.urlMethod,
      obj.httpStatus,
      obj.requestMessage,
      obj.responseMessage
    );
  }
}


export default LogEntry;