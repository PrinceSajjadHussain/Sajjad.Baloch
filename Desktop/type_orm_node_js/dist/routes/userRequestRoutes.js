"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const userRequestController_1 = require("../controller/userRequestController");
const router = (0, express_1.Router)();
router.get("/user_request", userRequestController_1.getUserRequests); // done error handling
router.get("/getAllAccounts/:id", userRequestController_1.getUserRequestsById); // done error handling
router.post("/getAccountDetail", userRequestController_1.getAccountDetailById); // done error handling
router.post('/user_request/:id', userRequestController_1.updateUserRequest); // done error handling
exports.default = router;
