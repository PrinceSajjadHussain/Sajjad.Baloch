"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createUser = void 0;
const typeorm_1 = require("typeorm");
const USER_REQUEST_1 = require("./entity/USER_REQUEST");
// import { USER_REQUEST } from './entity/USER_REQUEST';
function createUser(req, res) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            // Validate request body against USER_REQUEST fields
            const { ID, CREATED_BY_USER, CREATED_DATETIME, UPDATED_BY_USER, UPDATED_DATETIME, BOOL_SPARE1VAL, BOOL_SPARE2VAL, BOOL_SPARE3VAL, BOOL_SPARE4VAL, BOOL_SPARE5VAL, CREATED_BY, DATE_CREATED, INT_SPARE1VAL, INT_SPARE2VAL, INT_SPARE3VAL, INT_SPARE4VAL, INT_SPARE5VAL, IS_ENABLED, LAST_UPDATED, MODIFIED_BY, STR_SPARE1VAL, STR_SPARE2VAL, STR_SPARE3VAL, STR_SPARE4VAL, STR_SPARE5VAL, BACK_END_MODULE, MODULE_STATUS, STR_SPARE6VAL, STR_SPARE7VAL, DATE_SPARE1VAL, DATE_SPARE2VAL, DATE_SPARE3VAL, DATE_SPARE4VAL, DATE_SPARE5VAL, STR_SPARE8VAL, STR_SPARE9VAL, STR_SPARE10VAL, ROOM_ID, VIDEO_KYC_USER_ID, VIDEO_KYC_USER_NAME, OCR_COMPARISION, ACCOUNT_OPENING_DATE, PBC_EMAIL } = req.body;
            // Validate ID and CREATED_BY_USER using class-validator
            let user_request = new USER_REQUEST_1.USER_REQUEST();
            const user_req = req.body.USER_REQUEST;
            user_request = Object.assign(Object.assign({}, req.body), { USER_REQUEST: JSON.stringify(user_req) });
            // user.ID = ID;
            // user.CREATED_BY_USER = CREATED_BY_USER;
            // const errors = await validate(user);
            // if (errors.length > 0) {
            //   return res.status(400).json({ errors });
            // }
            // Establish database connection
            // const connection = await createConnection();
            // // Create user entity using TypeORM
            // const userRepository = connection.getRepository(USER_REQUEST);
            // const newUser = userRepository.create({
            //   ID,
            //   CREATED_BY_USER
            // });
            // // Save user entity
            // await userRepository.save(newUser);
            // await connection.close(); // Close connection after use
            const connection = (0, typeorm_1.getConnection)();
            const userRepository = connection.getRepository(USER_REQUEST_1.USER_REQUEST);
            yield userRepository.insert(user_request);
            // await connection.manager.save(user_request);
            // await connection.manager.save(user_request);
            res.status(201).send("User has been saved");
        }
        catch (err) {
            console.error('Error creating user:', err);
            return res.status(500).json({ error: 'Failed to create user' });
        }
    });
}
exports.createUser = createUser;
