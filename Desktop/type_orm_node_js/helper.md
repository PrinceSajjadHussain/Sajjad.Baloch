# TID Middleware

## Overview

`tidMiddleware` is an Express.js middleware function designed to generate and attach a unique Transaction ID (TID) to each HTTP request and response. This middleware is useful for tracking and logging individual requests, allowing for better debugging and monitoring of web applications.

## Features

- **Generate Unique TID**: Creates a unique Transaction ID for each request.
- **Attach TID to Request**: Adds the TID to the request headers (optional).
- **Include TID in Responses**: Adds the TID to all JSON responses, aiding in tracing and logging.

## Use

app.use(tidMiddleware);

## File

js_blink_backend/src/middleware/tidMiddleware.ts

-----------------------------------------------------------------------------------------------

## Method Filter Middleware

### Overview

The `methodFilter` middleware for Express.js restricts HTTP methods to a predefined set and logs any attempts to use methods that are not allowed. This middleware ensures that your API only accepts specific HTTP methods and provides detailed logs of disallowed requests for monitoring and debugging purposes.

### Features

- **Method Restriction**: Allows only `GET` and `POST` methods by default. You can modify the list of allowed methods as needed.
- **Logging**: Logs details about disallowed requests, including timestamp, HTTP method, URL, IP address, user agent, and transaction ID (TID), using the provided `winston` logger.

## Use
   
app.use(methodFilter(logger));

## File

js_blink_backend/src/middleware/methodFilter.ts

-----------------------------------------------------------------------------------------------

## Request Logger Middleware

### Overview

The `requestLogger` middleware for Express.js is designed to log details of incoming HTTP requests. It provides a way to log important request information, including modified request bodies, for debugging and monitoring purposes. This middleware uses a `winston` logger instance to output detailed logs for each request received by the server.

### Features

- **Customizable Request Body Logging**: Modifies specific properties in the request body for logging purposes, such as `base64`, `liveImage`, and `accountType`.
- **Detailed Logging**: Logs request details including timestamp, HTTP method, URL, IP address, user agent, transaction ID (TID), and the modified request body.
- **Integration with Winston**: Uses the provided `winston` logger instance for logging.

## Use
   
app.use(requestLogger(logger));

## File

js_blink_backend/src/middleware/requestLogger.ts

-----------------------------------------------------------------------------------------------

## Response Logger Middleware

### Overview

The `responseLogger` middleware for Express.js is designed to log details of HTTP responses. It enhances debugging and monitoring by capturing and logging response data, including specific fields and modifications based on request URL and response status. This middleware uses a `winston` logger instance to output detailed logs for each response sent by the server.

### Features

- **Customizable Response Body Logging**: Modifies specific properties in the response body based on the request URL and status.
- **Detailed Logging**: Logs response details including timestamp, HTTP method, URL, IP address, user agent, transaction ID (TID), and the modified response body.
- **Integration with Winston**: Uses the provided `winston` logger instance for logging.

## Use
   
app.use(responseLogger(logger));

## File

js_blink_backend/src/middleware/responseLogger.ts

-----------------------------------------------------------------------------------------------

## 404 Error Handler Middleware

### Overview

The `notFoundHandler` middleware for Express.js handles requests that do not match any defined routes, providing a custom 404 error response and logging details about the request. This middleware is useful for capturing and logging instances where clients attempt to access non-existent routes, helping with debugging and monitoring.

### Features

- **Custom 404 Response**: Returns a JSON response with a 404 status code and an error message indicating that the route was not found.
- **Detailed Logging**: Logs details about the 404 error, including the request method, URL, IP address, user agent, transaction ID (TID), and a custom log message, using a `winston` logger.

## Use
   
app.use(notFoundHandler(logger));

## File

js_blink_backend/src/middleware/notFoundHandler.ts

-----------------------------------------------------------------------------------------------

## Error Logger Middleware

### Overview

The `errorLogger` middleware for Express.js captures and logs details about unhandled errors that occur during the request-response cycle. This middleware is designed to provide detailed logging of errors, which is crucial for debugging and monitoring the health of your application. It uses a `winston` logger instance to record error details, making it easier to track and resolve issues.

### Features

- **Error Logging**: Captures and logs detailed information about errors, including the request method, URL, IP address, user agent, transaction ID (TID), and the error message.
- **Customizable Status Codes**: Logs the HTTP status code associated with the error.
- **Integration with Winston**: Utilizes the `winston` logger instance for logging error details.

## Use
   
app.use(errorLogger(logger));

## File

js_blink_backend/src/middleware/errorLogger.ts

-----------------------------------------------------------------------------------------------

## `generateUniqueId`

### Description

The `generateUniqueId` function generates a unique identifier based on the current date and time. This function creates a string that uniquely represents the exact moment it was called, making it useful for generating unique keys or IDs.

### How It Works

The function constructs a unique identifier by concatenating the following components:
1. **Year**: The current year (e.g., `2024`).
2. **Month**: The current month (1-based index, e.g., `9` for September).
3. **Day**: The current day of the month (e.g., `6`).
4. **Time**: The current time in milliseconds since the Unix epoch (e.g., `1694005200000`).

This combination ensures that the generated ID is unique because it includes the precise date and time down to milliseconds.

### Use

const uniqueId = generateUniqueId();

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `convertToDate`

### Description

The `convertToDate` function converts a date-time string in the format `"DD-MMM-YY hh.mm.ss[.SSS] AM/PM"` into a JavaScript `Date` object. This is useful for parsing and working with date-time strings that follow this specific format.

### Format

The input string should be in the following format:
- **DD**: Day of the month (e.g., `06`).
- **MMM**: Three-letter month abbreviation (e.g., `Sep` for September).
- **YY**: Two-digit year (e.g., `24` for 2024).
- **hh**: Hour in 12-hour format (e.g., `02`).
- **mm**: Minutes (e.g., `30`).
- **ss**: Seconds (e.g., `15`).
- **SSS**: Optional milliseconds (e.g., `123`).
- **AM/PM**: Period of the day (e.g., `PM`).

### Use

const date = convertToDate("06-Sep-24 02.30.15.123 PM");

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `generateRandomDigits`

### Description

The `generateRandomDigits` function generates a string of random digits of the specified length. This function is useful for creating random numeric strings, which can be used for purposes such as generating PIN codes, random IDs, or unique tokens.

### Parameters

- **`length`** (`number`): The desired length of the random digit string.

### Returns

- **`string`**: A string of random digits with the specified length.

### Use

const randomDigits = generateRandomDigits(5);

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `encryptText`

### Description

The `encryptText` function encrypts a JavaScript object into a Base64-encoded string using AES-128-CBC encryption. This function converts the object into a JSON string and encrypts it, returning the encrypted data as a Base64-encoded string.

**Note:** The key and initialization vector (IV) used in this example are not securely managed. For production use, ensure that you use a secure key management system and a unique, random IV for each encryption operation.

### Parameters

- **`data`** (`object`): The JavaScript object that you want to encrypt.

### Returns

- **`string`**: The encrypted data encoded as a Base64 string.

### Use

const data = { name: 'Alice', age: 30 };
const encryptedData = encryptText(data);

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `decryptText`

### Description

The `decryptText` function decrypts a Base64-encoded string that was encrypted using AES-128-CBC encryption. It converts the Base64-encoded encrypted string back into the original JavaScript object.

**Note:** The key and initialization vector (IV) used in this function must match those used during encryption. Ensure secure key management and use a unique, random IV for each encryption operation in a production environment.

### Parameters

- **`encryptedData`** (`string`): The Base64-encoded string that contains the encrypted data to decrypt.

### Returns

- **`object`**: The decrypted JavaScript object.

### Use

const encryptedData = 'Base64EncodedEncryptedString';
const decryptedData = decryptText(encryptedData);

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `objectToBase64Node`

### Description

The `objectToBase64Node` function converts a JavaScript object into a Base64-encoded string. This function serializes the object into a JSON string and then encodes it in Base64 format. It is useful for scenarios where you need to represent object data in a text-based format for easy transmission or storage.

### Parameters

- **`obj`** (`object`): The JavaScript object that you want to convert to a Base64-encoded string.

### Returns

- **`string`**: The Base64-encoded string representing the serialized JavaScript object.

### Use

const obj = { name: 'Alice', age: 30 };
const base64String = objectToBase64Node(obj);

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `base64ToObject`

### Description

The `base64ToObject` function decodes a Base64-encoded string that represents a JSON-encoded object and converts it back into a JavaScript object. It handles the conversion from Base64 to a binary string, then to a `Uint8Array`, and finally decodes it into a UTF-8 string which is parsed into an object.

If the decoding or parsing process fails, an error is logged and `null` is returned.

### Parameters

- **`base64String`** (`string`): The Base64-encoded string that represents the serialized object.

### Returns

- **`object|null`**: The decoded JavaScript object if successful; otherwise, `null` if an error occurs during decoding or parsing.

### Use

const base64String = 'eyJuYW1lIjoiQWxpY2UiLCJhZ2UiOjMwfQ==';
const obj = base64ToObject(base64String);

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `exisitingUserResponseText`

### Description

The `exisitingUserResponseText` function returns a specific response message based on the input text. It is designed to handle cases where a predefined input corresponds to a "Success" message, while all other inputs receive a "Username and CNIC already Exist" message.

### Parameters

- **`Text`** (`string`): The input string to be checked against predefined values.

### Returns

- **`string`**: A response message based on the input text.

### Use

const response1 = exisitingUserResponseText("bS4m1W6XMWXehlLZbvzLR6n/J2c0GzEurkQhB925nd5shP8otg4YKYY6PsXlipt5dBCevpeciw67tB/zNkreZAu0hFy/SujybVSkk7p7LHqblwSSb0yBjwz0p1V5FHOniX12IXH7AEOEgSH7GypT9A==");

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `generateTID`

### Description

The `generateTID` function generates a unique Transaction ID (TID) by combining the current date with a random 12-digit number. The TID format is `YYYYMMDD-XXXXXXXXXXXX`, where:

- `YYYYMMDD` is the current date in year-month-day format.
- `XXXXXXXXXXXX` is a random 12-digit number.

This format ensures that the TID is unique and sortable by date, making it useful for tracking transactions or records.

### Returns

- **`string`**: The generated Transaction ID in the format `YYYYMMDD-XXXXXXXXXXXX`.

### Use

const tid = generateTID();

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `getNextTraceNo`

### Description

The `getNextTraceNo` function generates and returns the next trace number in a zero-padded 6-digit format. This function is used to create unique sequential trace numbers for tracking or identification purposes. Each call to this function increments the trace number and ensures that the trace number is always a 6-digit string, padded with leading zeros if necessary.

### Important

- **`currentTraceNo`**: This variable must be defined and initialized elsewhere in your code. It tracks the current trace number and is incremented each time `getNextTraceNo` is called.

### Returns

- **`string`**: The next trace number, zero-padded to 6 digits.

### Use

let currentTraceNo = 1;
getNextTraceNo(); 

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `formatDateToCustomString`

### Description

The `formatDateToCustomString` function generates a string representing the current date and time in the format `YYYYMMDDHHMMSS`. This format provides a compact and sortable representation of the current timestamp, which can be useful for generating unique identifiers or timestamps.

### Returns

- **`string`**: The formatted date and time string in the `YYYYMMDDHHMMSS` format.

### Use

const formattedDate = formatDateToCustomString();

## File

js_blink_backend/src/utils/helpers.ts

-----------------------------------------------------------------------------------------------

## `getLOVs`

### Description

The `getLOVs` function reads and parses the List of Values (LOVs) from a JSON file located at `../../lovs_list/LOVs.json`. It returns the parsed JSON object. This function is useful for retrieving configuration or reference data stored in the JSON format.

### Returns

- **`object`**: The parsed JSON object from the `LOVs.json` file.

### Throws

- **`Error`**: Throws an error with the message "Failed to fetch LOVs" if there is an issue reading or parsing the file.

### Use

const lovs = getLOVs();

## File

js_blink_backend/src/utils/lovsUtils.ts

-----------------------------------------------------------------------------------------------

## `getProductType`

### Description

The `getProductType` function reads and parses product type data from a JSON file located at `../../lovs_list/Product_Type.json`. It returns the parsed JSON object. This function is useful for retrieving configuration or reference data related to product types stored in JSON format.

### Returns

- **`object`**: The parsed JSON object from the `Product_Type.json` file.

### Throws

- **`Error`**: Throws an error with the message "Failed to fetch Product Type" if there is an issue reading or parsing the file.

### Use

const productTypes = getProductType();
 
## File

js_blink_backend/src/utils/lovsUtils.ts

-----------------------------------------------------------------------------------------------

## `successResponse`

### Description

The `successResponse` function generates a standardized response object used to indicate a successful operation. This function includes a status code, a message, and optional data. If no status code is provided, it defaults to "00". If no message is provided, it defaults to "Success".

### Parameters

- **`data`** (`any`): The data to include in the response. This can be any type (e.g., object, array).
- **`message`** (`string`, optional): The message to include in the response. Defaults to `"Success"` if not provided.
- **`code`** (`any`, optional): An optional status code to include in the response. Defaults to `"00"` if not provided.

### Returns

- **`object`**: The success response object with the following structure:
  - `status`: The status code (`string`). Defaults to `"00"`.
  - `message`: The message (`string`). Defaults to `"Success"`.
  - `data`: The data provided as input.

### Use

const response = successResponse({ id: 123 }, "Operation completed", "01");

## File

js_blink_backend/src/utils/responseUtils.ts

-----------------------------------------------------------------------------------------------

## `errorResponse`

### Description

The `errorResponse` function generates a standardized error response object used to indicate a failed operation. This function includes a status code, a message, and optional error data. If no status code is provided, it defaults to `"01"`. If no message is provided, it defaults to `"Error"`.

### Parameters

- **`error`** (`any`): The error information to include in the response. This can be any type (e.g., object, string).
- **`message`** (`string`, optional): The message to include in the response. Defaults to `"Error"` if not provided.
- **`code`** (`any`, optional): An optional status code to include in the response. Defaults to `"01"` if not provided.

### Returns

- **`object`**: The error response object with the following structure:
  - `status`: The status code (`string`). Defaults to `"01"`.
  - `message`: The message (`string`). Defaults to `"Error"`.
  - `data`: The error information provided as input.

### Use

const response = errorResponse({ message: "Invalid input" }, "Validation failed", "02");

## File

js_blink_backend/src/utils/responseUtils.ts

