// import swaggerJsdoc from 'swagger-jsdoc';
// import swaggerUi from 'swagger-ui-express';
// import express from 'express';
// // import lovsroutes from "./src/routes/lovsRoutes"
// // Define the Swagger options
// const swaggerOptions = {
//   swaggerDefinition: {
//     openapi: '3.0.0', // or '2.0' if you're using Swagger 2.0
//     info: {
//       title: 'JS Blink  ',
//       version: '1.0.0',
//       description: 'Description of your API',
//     },
//     servers: [
//       {
//         url: 'https://localhost:3005/api', // Adjust this to your server URL
//         description: 'Local development server',
//       },
//     ],
//   },
//   apis: ['./src/routes/lovsRoutes.ts'], // Path to the specific API docs file
// };

// // Initialize Swagger JSDoc
// const swaggerSpec = swaggerJsdoc(swaggerOptions);

// const setupSwagger = (app: express.Express) => {
//   // Serve Swagger API docs
//   app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
// };

// export default setupSwagger;
