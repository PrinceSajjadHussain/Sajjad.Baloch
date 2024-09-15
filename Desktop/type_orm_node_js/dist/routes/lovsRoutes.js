"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const lovsController_1 = require("../controller/lovsController");
const router = (0, express_1.Router)();
router.get('/lovs', lovsController_1.getLOVsController);
/**
 * @swagger
 * tags:
 *   name: LOVs
 *   description: Endpoints for managing LOVs and product types
 */
/**
 * @swagger
 * /lovs:
 *   get:
 *     summary: Retrieve all LOVs
 *     tags: [LOVs]
 *     responses:
 *       200:
 *         description: A list of LOVs
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   description: The status of the response
 *                   example: "00"
 *                 message:
 *                   type: string
 *                   description: A message describing the status
 *                   example: "Success"
 *                 data:
 *                   type: object
 *                   properties:
 *                     lovs:
 *                       type: object
 *                       properties:
 *                         genderList:
 *                           type: array
 *                           items:
 *                             type: object
 *                             properties:
 *                               key:
 *                                 type: string
 *                                 description: The gender key
 *                                 example: "Male"
 *                               value:
 *                                 type: string
 *                                 description: The gender value
 *                                 example: "Male"
 *                       example: {
 *                         "genderList": [
 *                           {
 *                             "key": "Male",
 *                             "value": "Male"
 *                           },
 *                           {
 *                             "key": "Female",
 *                             "value": "Female"
 *                           }
 *                         ]
 *                       }
 *       500:
 *         description: Internal server error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   description: Error status
 *                   example: "01"
 *                 message:
 *                   type: string
 *                   description: Error message
 *                   example: "An error occurred"
 */
exports.default = router;
