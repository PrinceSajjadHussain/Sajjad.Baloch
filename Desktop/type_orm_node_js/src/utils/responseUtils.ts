export const successResponse = (data: any, message = "Success",code?:any) => {
    return {
      status: code ?  code : "00",
      message: message,
      data: data
    };
  };
  
  export const errorResponse = (error: any, message = "Error",code?:any) => {
    return {
      status: code ?  code : "01",
      message: message,
      data: error
    };
  };
  