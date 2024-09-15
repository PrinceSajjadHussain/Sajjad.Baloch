import { getConnection, In } from "typeorm";
import { LOCAL_USER_REQUEST } from "../entity/LOCAL_USER_REQUEST";

export const findAllUserRequests = async () => {
  try {
    const userRepository = getConnection().getRepository(LOCAL_USER_REQUEST);
    return userRepository.find({
      where: { BACK_END_MODULE: "25" }, order: {
        CREATED_DATETIME: 'ASC'
      }
    });

  } catch (error: any) {
    console.error("Error fetching All Accounts:", error.message)
    throw new Error("Failed to fetch all Blinks accounts")
  }
};

export const findUserRequestsByID = async (ID: string) => {
  try {
    const userRepository = getConnection().getRepository(LOCAL_USER_REQUEST);
    return userRepository.find({
      where: { STR_SPARE1VAL: ID, BACK_END_MODULE: '25', MODULE_STATUS: In([1, 2, 3, 4, 5, 6]) }, order: {
        CREATED_DATETIME: 'ASC'
      }
    });
  } catch (error: any) {
    console.error(`Error fetching accounts by ID ${ID} :`, error.message)
    throw new Error(`Failed to fetch accounts by ID ${ID}`)
  }
};

export const findUserRequestByUniqueID = async (ID: string) => {
  try {
    debugger
    const userRepository = getConnection().getRepository(LOCAL_USER_REQUEST);
    return userRepository.find({ where: { ID: ID, BACK_END_MODULE: '25' } });

  } catch (error: any) {
    console.error(`Error fetching account by ID ${ID} :`, error.message)
    throw new Error(`Failed to fetch account by ID ${ID}`)

  }
};



export const userAccountDetailsInProduct = async (ID: string) => {
  try {
    const userRepository = getConnection().getRepository(LOCAL_USER_REQUEST);
    return userRepository.find({ where: { ID: ID, BACK_END_MODULE: '25' } });
  } catch (error: any) {
    console.error(`Error fetching account details by ID ${ID} :`, error.message)
    throw new Error("Error fetching account details by ID")
  }

};

