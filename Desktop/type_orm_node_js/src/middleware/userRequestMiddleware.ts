import { Client } from '@elastic/elasticsearch';
import { getUserRequestsService } from '../services/userRequestService';

// Create a new Elasticsearch client
const client = new Client({
    node: 'http://localhost:9200',
});

// Define the index name
const indexName = 'user-request';

const moduleStatusLabeling = (status: number) => {
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
}

export async function sendToElasticsearch() {
    try {
        const users = await getUserRequestsService();

        // yahan par users main poora data araha hai
        // yahan say har aik request ki ID nikalo gay aur apna alag object banao gay
        // jis main ID, module_Number, module_status, update_date_time and than
        // user_request ka column hoga
        // ooper jo object banay ga wo add hoga neechay code main
        // for each ka loop laga do yahan please
        let response: any;
        users.forEach(async element => {
            let elasticUserRequest = JSON.parse(element.USER_REQUEST);
            if(elasticUserRequest){
                const status = await moduleStatusLabeling(element.MODULE_STATUS)
                response = await client.index({
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
                })
    
            }


        });


        console.log('Document indexed successfully');
    } catch (error: any) {
        console.error('Error indexing document:', error.meta.body);
    }
}
