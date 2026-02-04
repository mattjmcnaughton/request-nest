import { ApiProvider } from "./contexts";
import { RealBinApiClient } from "./api";
import { BinsIndex } from "./pages";

const apiClient = new RealBinApiClient();

function App() {
  return (
    <ApiProvider client={apiClient}>
      <BinsIndex />
    </ApiProvider>
  );
}

export default App;
