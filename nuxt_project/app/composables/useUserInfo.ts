export const useUserInfo = () => {
  // simple local mock user state
  const userInfo = useState("userInfo", () => {
    return {
      id: "1",
      full_name: "Demo User",
      email: "demo@example.com"
    }
  })

  async function setUserInfo() {
    // no database call
    return
  }

  return { userInfo, setUserInfo }
}