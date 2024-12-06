<script>
import dayjs from "dayjs";
import Datepicker from "vue3-datepicker";
import { ref } from "vue";

export default {
  components: {
    "date-picker": Datepicker,
  },

  props: {
    modelValue: Object,
    minDate: Number,
  },
  emits: ["update:modelValue"],

  data() {
    return {
      rangeOrder: [
        "yesterday",
        "today",
        "thisweek",
        "lastweek",
        "thismonth",
        "lastmonth",
        "last3months",
        "last6months",
        "last1year",
        "last3year",
        //"custom",
      ],
      rangeTypeOptions: {
        yesterday: "Yesterday",
        today: "Today",
        thisweek: "This Week",
        lastweek: "Last Week",
        thismonth: "This Month",
        lastmonth: "Last Month",
        last3months: "Last 3 Months",
        last6months: "Last 6 Months",
        last1year: "Last 1 Year",
        last3year: "Last 3 Years",
        //custom: "Custom Date Range",
      },
      selectedRangeType: null,
      fromPickedDate: ref(new Date()),
      toPickedDate: ref(new Date()),
      disabledDates: {
        from: dayjs().startOf("day").add(1, "days").toDate(), // for datepicker do not show dates after today
      },
    };
  },

  computed: {
    rangeOrderFiltered() {
      // basic idea = don't show date range options when the range doesn't exist in dataset
      // i.e. if there aren't any orders older than 6 mos, don't show "last 3 years" as an option
      const rangeOrder = [];
      const minDate = this.minDate || 0;
      for (let i = 0; i < this.rangeOrder.length; i++) {
        const range = this.calculateRangeForType(this.rangeOrder[i]);
        if (!range || (range && range.asInt && range.asInt > minDate)) {
          rangeOrder.push(this.rangeOrder[i]);
        } else {
          rangeOrder.push(this.rangeOrder[i]);
          rangeOrder.push("custom");
          break;
        }
      }
      return rangeOrder;
    },
  },

  mounted() {
    this.updateComponentWithValue(this.modelValue);
  },

  methods: {
    calculateRangeForType(rangeType) {
      switch (rangeType) {
        case "yesterday":
          return {
            from: dayjs().subtract(1, "day").startOf("day").toDate(),
            to: dayjs().subtract(1, "day").startOf("day").toDate(),
            asInt: parseInt(dayjs().subtract(1, "day").format("YYYYMMDD")),
          };

        case "today":
          return {
            from: dayjs().startOf("day").toDate(),
            to: dayjs().endOf("day").toDate(),
            asInt: parseInt(dayjs().startOf("day").format("YYYYMMDD")),
          };

        case "thisweek":
          return {
            from: dayjs().startOf("week").toDate(),
            to: dayjs().endOf("week").toDate(),
            asInt: parseInt(dayjs().startOf("week").format("YYYYMMDD")),
          };

        case "lastweek":
          return {
            from: dayjs().subtract(1, "week").startOf("week").toDate(),
            to: dayjs().subtract(1, "week").endOf("week").toDate(),
            asInt: parseInt(dayjs().subtract(1, "week").format("YYYYMMDD")),
          };

        case "thismonth":
          return {
            from: dayjs().startOf("month").toDate(),
            to: dayjs().endOf("month").toDate(),
            asInt: parseInt(dayjs().startOf("month").format("YYYYMMDD")),
          };

        case "lastmonth":
          return {
            from: dayjs().subtract(1, "month").startOf("month").toDate(),
            to: dayjs().subtract(1, "month").endOf("month").toDate(),
            asInt: parseInt(dayjs().subtract(1, "month").format("YYYYMMDD")),
          };

        case "last3months":
          return {
            from: dayjs().subtract(3, "month").startOf("month").toDate(),
            to: dayjs().endOf("month").toDate(),
            asInt: parseInt(dayjs().subtract(3, "month").format("YYYYMMDD")),
          };

        case "last6months":
          return {
            from: dayjs().subtract(6, "month").startOf("month").toDate(),
            to: dayjs().endOf("month").toDate(),
            asInt: parseInt(dayjs().subtract(6, "month").format("YYYYMMDD")),
          };

        case "last1year":
          return {
            from: dayjs().subtract(1, "year").startOf("year").toDate(),
            to: dayjs().endOf("year").toDate(),
            asInt: parseInt(dayjs().subtract(1, "year").format("YYYYMMDD")),
          };

        case "last3year":
          return {
            from: dayjs().subtract(3, "year").startOf("year").toDate(),
            to: dayjs().endOf("year").toDate(),
            asInt: parseInt(dayjs().subtract(3, "year").format("YYYYMMDD")),
          };

        default:
          return null;
      }
    },

    dateRangeChanged(rangeType) {
      if (this.selectedRangeType === "custom") {
        if (this.fromPickedDate == null || this.toPickedDate == null) {
          return;
        } else {
          let dateRange = {
            from: dayjs(this.fromPickedDate).startOf("day").toDate(),
            to: dayjs(this.toPickedDate).endOf("day").toDate(),
          };

          this.$emit("update:modelValue", dateRange);
        }
      } else {
        let dateRange = this.calculateRangeForType(rangeType);
        this.$emit("update:modelValue", dateRange);
      }
    },

    updateComponentWithValue(newValue) {
      if (!newValue) {
        this.selectedRangeType = null;
        this.fromPickedDate = null;
        this.toPickedDate = null;
      } else {
        var rangeTypes = Object.keys(this.rangeTypeOptions);
        for (var i = 0; i < rangeTypes.length; i++) {
          let preSetRange = this.calculateRangeForType(rangeTypes[i]);

          if (preSetRange === null) {
            continue;
          }

          if (
            newValue.from.getTime() === preSetRange.from.getTime() &&
            newValue.to.getTime() === preSetRange.to.getTime()
          ) {
            this.selectedRangeType = rangeTypes[i];
            this.fromPickedDate = null;
            this.toPickedDate = null;
            return;
          }
        }

        // If newValue didn't match any of the pre-set values then it's a custom value
        this.selectedRangeType = "custom";
        this.fromPickedDate = newValue.from;
        this.toPickedDate = newValue.to;
      }
    },
  },

  watch: {
    modelValue: {
      immediate: true,
      handler(newValue) {
        this.updateComponentWithValue(newValue);
      },
    },
  },
};
</script>

<template>
  <div class="w-100 position-relative">
    <form>
      <select
        class="form-select w-auto"
        v-model="selectedRangeType"
        @change="
          (event) => {
            dateRangeChanged(event.target.value);
          }
        "
      >
        <option v-for="range in rangeOrderFiltered" :key="range" :value="range">
          {{ rangeTypeOptions[range] }}&nbsp;&nbsp;&nbsp;
        </option>
      </select>

      <date-picker
        v-if="selectedRangeType == 'custom'"
        v-model="fromPickedDate"
        @input="dateRangeChanged('custom')"
        input-class="form-control mt-2"
        :disabledDates="disabledDates"
        placeholder="From"
        :calendar-button="true"
        calendar-button-icon="fa fa-calendar"
      ></date-picker>

      <date-picker
        v-if="selectedRangeType == 'custom'"
        v-model="toPickedDate"
        @input="dateRangeChanged('custom')"
        input-class="form-control mt-2"
        :disabledDates="disabledDates"
        placeholder="To"
        :calendar-button="true"
        calendar-button-icon="fa fa-calendar"
      ></date-picker>
    </form>
  </div>
</template>
