import { BrowserRouter, Routes, Route } from "react-router";
import { ApiProvider } from "./contexts";
import { RealBinApiClient } from "./api";
import { Layout } from "./components";
import { BinsIndex, BinDetail, EventDetail } from "./pages";

const apiClient = new RealBinApiClient();

function App() {
  return (
    <BrowserRouter>
      <ApiProvider client={apiClient}>
        <Layout>
          <Routes>
            <Route path="/" element={<BinsIndex />} />
            <Route path="/bins/:binId" element={<BinDetail />} />
            <Route path="/events/:eventId" element={<EventDetail />} />
          </Routes>
        </Layout>
      </ApiProvider>
    </BrowserRouter>
  );
}

export default App;
