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
exports.sendToElasticsearch = sendToElasticsearch;
const elasticsearch_1 = require("@elastic/elasticsearch");
const userRequestService_1 = require("../services/userRequestService");
// Create a new Elasticsearch client
const client = new elasticsearch_1.Client({
    node: 'http://localhost:9200',
});
// Define the index name
const indexName = 'user-request';
const moduleStatusLabeling = (status) => {
    switch (status) {
        case 0:
            return "Reset";
        case 1:
            return "Smart CNIC Extracted";
        case 2:
            return "Urdu NIC Extracted";
        case 3:
            return "Face Verified";
        case 4:
            return "OTP Verification Pending";
        case 5:
            return "OTP Verified";
        case 6:
            return "Incompleted Request";
        case 7:
            return "Submitted Request";
        default:
            return "";
    }
};
function sendToElasticsearch() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const users = yield (0, userRequestService_1.getUserRequestsService)();
            // yahan par users main poora data araha hai
            // yahan say har aik request ki ID nikalo gay aur apna alag object banao gay
            // jis main ID, module_Number, module_status, update_date_time and than
            // user_request ka column hoga
            // ooper jo object banay ga wo add hoga neechay code main
            // for each ka loop laga do yahan please
            let response;
            users.forEach((element) => __awaiter(this, void 0, void 0, function* () {
                let elasticUserRequest = JSON.parse(element.USER_REQUEST);
                if (elasticUserRequest) {
                    const status = yield moduleStatusLabeling(element.MODULE_STATUS);
                    response = yield client.index({
                        index: indexName,
                        body: {
                            // user_request: JSON.parse(element.USER_REQUEST),
                            id: element.ID,
                            timestamp: element.UPDATED_DATETIME,
                            account_type: element.STR_SPARE10VAL,
                            module_status: status,
                            primaryDetails: elasticUserRequest.primaryDetails,
                            basicDetails: elasticUserRequest.basicDetails,
                            sourceOfIncomeDetails: elasticUserRequest.sourceOfIncomeDetails,
                            documentUploadDetail: elasticUserRequest.documentUploadDetail,
                        },
                    });
                }
            }));
            console.log('Document indexed successfully');
        }
        catch (error) {
            console.error('Error indexing document:', error.meta.body);
        }
    });
}
