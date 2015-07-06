
export default function Shout(toastr,toastrConfig) {
  angular.extend(toastrConfig, {
    allowHtml: false,
    closeButton: true,
    extendedTimeOut: 1000,
    newestOnTop: true,
    tapToDismiss: true,
    timeOut: 5000,
  });
  return {
    error: (msg, heading,response) => {
      toastr.error(msg, heading);
    },
    success: (msg, heading,response) => {
      toastr.success(msg, heading);
    },
    info: (msg, heading,response) => {
      toastr.info(msg, heading);
    },
    vError: (err) => {
      console.log(err);
      if(err.data && err.data.error && err.data.error.message)
        toastr.error(err.data.error.message, "Error");
    },
    sSuccess: (message) => {
      toastr.success(message, "Success");
    },
    sInfo: (message) => {
      toastr.info(message, "Info");
    }
  };
}
