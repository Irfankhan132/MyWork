<script setup lang="ts">
import type { DropdownItem } from "#ui/types";

const { userInfo } = useUserInfo();
const toast = useToast();

// Simulate logged-in state
const user = computed(() => userInfo.value);

const items: DropdownItem[][] = [
  [
    {
      label: user.value?.email || "",
      slot: "account",
      disabled: true,
    },
    {
      label: "Profile",
      click: toProfile,
    },
    {
      label: "Create Recipe",
      to: "/recipes/create",
    },
  ],
  [
    {
      label: "Sign out",
      icon: "i-mdi-logout",
      click: logout,
    },
  ],
];

function toProfile() {
  navigateTo(`/profile/${user.value?.id}`);
}

function logout() {
  // Fake logout (clear mock user)
  userInfo.value = null as any;
  navigateTo("/");
  toast.add({
    title: "Logged out",
  });
}
</script>