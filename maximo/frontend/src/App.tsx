import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import AssetDetail from "./pages/AssetDetail";
import WorkOrders from "./pages/WorkOrders";
import WorkOrderDetail from "./pages/WorkOrderDetail";
import PreventiveMaintenance from "./pages/PreventiveMaintenance";
import ServiceRequests from "./pages/ServiceRequests";
import InventoryPage from "./pages/Inventory";
import Purchasing from "./pages/Purchasing";
import Health from "./pages/Health";
import Monitor from "./pages/Monitor";
import Predict from "./pages/Predict";
import Visual from "./pages/Visual";
import Assist from "./pages/Assist";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/assets/:id" element={<AssetDetail />} />
        <Route path="/workorders" element={<WorkOrders />} />
        <Route path="/workorders/:id" element={<WorkOrderDetail />} />
        <Route path="/pm" element={<PreventiveMaintenance />} />
        <Route path="/servicerequests" element={<ServiceRequests />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/purchasing" element={<Purchasing />} />
        <Route path="/ai/health" element={<Health />} />
        <Route path="/ai/monitor" element={<Monitor />} />
        <Route path="/ai/predict" element={<Predict />} />
        <Route path="/ai/visual" element={<Visual />} />
        <Route path="/ai/assist" element={<Assist />} />
      </Routes>
    </Layout>
  );
}
