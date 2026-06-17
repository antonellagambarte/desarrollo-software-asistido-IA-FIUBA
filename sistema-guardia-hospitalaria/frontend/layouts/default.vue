<template>
  <v-app>
    <v-navigation-drawer permanent width="220" color="primary">
      <div class="d-flex flex-column" style="height: 100%">
        <div>
          <div class="pa-4 pb-3">
            <div class="text-subtitle-2 font-weight-bold text-white opacity-90">
              Guardia Hospitalaria
            </div>
          </div>
          <v-divider color="rgba(255,255,255,0.25)" />
          <v-list nav density="compact" class="mt-2" bg-color="transparent">
            <v-list-item
              v-for="item in mainItems"
              :key="item.label"
              :prepend-icon="item.icon"
              :title="item.label"
              rounded="lg"
              base-color="white"
              :to="item.to || undefined"
              @click="item.onClick && item.onClick()"
            />
          </v-list>
        </div>

        <div class="mt-auto">
          <v-divider v-if="footerItems.length" color="rgba(255,255,255,0.25)" />
          <v-list nav density="compact" class="mb-2" bg-color="transparent">
            <v-list-item
              v-for="item in footerItems"
              :key="item.label"
              :prepend-icon="item.icon"
              :title="item.label"
              rounded="lg"
              base-color="white"
              :to="item.to || undefined"
              @click="item.onClick && item.onClick()"
            />
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup>
import { computed } from 'vue'
import { useSidebarItems } from '~/composables/useSidebarItems'

const { items: sidebarItems } = useSidebarItems()

const mainItems = computed(() => sidebarItems.value.filter(i => !i.footer))
const footerItems = computed(() => sidebarItems.value.filter(i => i.footer))
</script>
