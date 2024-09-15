import fs from 'fs/promises';
import path from 'path';
import { getConnection } from "typeorm";
import { LOCAL_USER_REQUEST } from "../entity/LOCAL_USER_REQUEST";
import { findAllUserRequests, findUserRequestsByID, userAccountDetailsInProduct, } from "../queries/userRequestQueries";

const assetsDir = path.resolve(__dirname, '../../assets');

export const getUserRequestsService = async () => {
  try {
    return findAllUserRequests();
  } catch (error: any) {
    console.error("Error fetching All Accounts:", error.message);
    throw new Error(error.message)
  }
};

export const getUserRequestsByIdService = async (ID: string) => {
  try {
    return findUserRequestsByID(ID);
  } catch (error: any) {
    console.error(`Error fetching accounts by ID ${ID} :`, error.message)
    throw new Error(error.message)

  }
};

export const getAccountDetailByIdService = async (ID: string) => {
  try {
    return userAccountDetailsInProduct(ID);
  } catch (error: any) {
    console.error(`Error fetching account details by ID ${ID} :`, error.message)
    throw new Error(error.message)
  }
}

export const getCnicFrontByIdService = async (id: string) => {
  try {
    const fileDir = path.resolve(assetsDir, id.toString());
    const files = await fs.readdir(fileDir);
    for (const file of files) {
      const filePath = path.resolve(fileDir, file);
      const lastDotIndex = file.lastIndexOf('.');
      const baseName = file.slice(0, lastDotIndex);
      const extension = file.slice(lastDotIndex + 1);
      if (baseName === 'cnicFront') {
        const cnicFrontData = await fs.readFile(filePath, 'base64');
        return { id, cnicFront: cnicFrontData };
      }
    }

    throw new Error('Cnic Front Image not found');

  } catch (error: any) {
    const errMsg = error.message === "Cnic Front Image not found" ? error.message : "The specified ID doesn't exist."
    throw new Error(errMsg);

  }
};


export const updateUserRequestService = async (id: any, userRequestData: any) => {
  try {
    const connection = getConnection();
    const userRequestRepository = connection.getRepository(LOCAL_USER_REQUEST);

        const partialUserRequest = new LOCAL_USER_REQUEST();
        Object.assign(partialUserRequest, userRequestData);
        partialUserRequest.USER_REQUEST = JSON.stringify(userRequestData.USER_REQUEST);
        const temp = await userRequestRepository.update(id, {
          ...userRequestData,
          USER_REQUEST: JSON.stringify(userRequestData.USER_REQUEST),

        });

        return { ID:id}

  } catch (error: any) {
    console.error(`Error occurred while updating account details for ID ${id} :`, error.message);
    throw new Error(`Failed to update account details for ID ${id}`)

  }

};
