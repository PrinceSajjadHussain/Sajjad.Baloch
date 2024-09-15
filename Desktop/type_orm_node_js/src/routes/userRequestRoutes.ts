import { Router } from "express";
import { getUserRequests, updateUserRequest, getUserRequestsById, getAccountDetailById } from "../controller/userRequestController";
const router = Router();

router.get("/user_request", getUserRequests); // done error handling
router.get("/getAllAccounts/:id", getUserRequestsById); // done error handling
router.post("/getAccountDetail", getAccountDetailById); // done error handling
router.post('/user_request/:id', updateUserRequest);  // done error handling



export default router;
