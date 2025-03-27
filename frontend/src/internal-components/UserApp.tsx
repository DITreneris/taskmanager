import { AppProvider } from "components/AppProvider";
import { Outlet } from "react-router-dom";

export const UserApp = () => {
  return (
    <AppProvider>
      <Outlet />
    </AppProvider>
  );
};
