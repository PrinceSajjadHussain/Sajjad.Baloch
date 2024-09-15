import { Request, Response } from "express";
import { getUserRequestsService, updateUserRequestService, getUserRequestsByIdService, getAccountDetailByIdService } from "../services/userRequestService";
import { successResponse, errorResponse } from "../utils/responseUtils";


export const getUserRequests = async (req: Request, res: Response) => {
  try {
    const users = await getUserRequestsService();
    res.status(200).json(successResponse(users));
  } catch (error: any) {
    console.error("Error fetching All Accounts:", error.message);
    res.status(500).json(errorResponse(error.message));
  }
};

export const getUserRequestsById = async (req: Request, res: Response) => {
  const { id } = req.params;
  try {
    const accountsList = await getUserRequestsByIdService(id);
    if (accountsList.length > 0) {
      const filterList = accountsList.filter(item => item.STR_SPARE4VAL)
      if (filterList.length > 0) {
        res.status(200).json(successResponse(filterList))

      } else {
        const errorMessage = `Failed to fetching accounts by ID ${id}`
        console.error(`Error fetching accounts by ID ${id} :`, errorMessage)
        res.status(500).json(errorResponse(errorMessage));
      }
    } else {
      const errorMessage = `ID Number ${id} does not exist.`
      console.error(`Error fetching accounts by ID ${id} :`, errorMessage)
      res.status(500).json(errorResponse(errorMessage));
    }
  } catch (error: any) {
    console.error(`Error fetching accounts by ID ${id} :`, error.message)
    res.status(500).json(errorResponse(error.message));
  }
};

export const getAccountDetailById = async (req: Request, res: Response) => {
  const { id } = req.body;
  try {
    const users = await getAccountDetailByIdService(id);

    if (users.length > 0) {
      res.status(200).json(successResponse(users[0]));

    } else {
      const errorMessage = `ID Number ${id} does not exist.`
      console.error(`Error fetching account details by ID ${id} :`, errorMessage);
      res.status(500).json(errorResponse(errorMessage));
    }


  } catch (error: any) {
    console.error(`Error fetching account details by ID ${id} :`, error.message);
    res.status(500).json(errorResponse(error.message));
  }
};



export const updateUserRequest = async (req: Request, res: Response) => {
  const { id } = req.params;
  try {
    if (!id) {
      console.error(`Error occurred while updating account details for ID ${id} :`, "Id is Missing");
      throw new Error("Id is Missing")
    }

    const result = await updateUserRequestService(id, req.body);
    res.status(200).json(successResponse(result));

  } catch (error: any) {
    const safeError = typeof error?.message === "object" ? JSON.parse(error?.message ? error?.message : error) : error?.message;
    console.error(`Error occurred while updating account details for ID ${id} :`, safeError);
    res.status(500).json(errorResponse(safeError, `Failed to update account details for ID ${id}`));

  }
};
