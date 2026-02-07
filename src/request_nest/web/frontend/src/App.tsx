import { BrowserRouter, Routes, Route } from "react-router";
import { ApiProvider } from "./contexts";
import { RealBinApiClient } from "./api";
import { BinsIndex, BinDetail, EventDetail } from "./pages";

const apiClient = new RealBinApiClient();

function App() {
  return (
    <BrowserRouter>
      <ApiProvider client={apiClient}>
        <Routes>
          <Route path="/" element={<BinsIndex />} />
          <Route path="/bins/:binId" element={<BinDetail />} />
          <Route path="/events/:eventId" element={<EventDetail />} />
        </Routes>
      </ApiProvider>
    </BrowserRouter>
  );
}

export default App;
