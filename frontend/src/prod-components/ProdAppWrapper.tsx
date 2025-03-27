import { UserApp } from "../internal-components/UserApp.js";

/**
 * Just a wrapper for the app. This is used in production mode.
 * This is required because we need to use the react-router <Outlet /> component
 * to make this work nice with the dev mode.
 */
export default function ProdAppWrapper() {
  return <UserApp />;
}
