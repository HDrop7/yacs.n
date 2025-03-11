<template>
  <b-container fluid>
    <b-breadcrumb :items="breadcrumbNav"></b-breadcrumb>
    <div v-if="!isLoadingCourses && courseObj" class="w-90 ml-4 mb-4">
      <b-row>
        <b-col>
          <h1 class="mt-4">{{ courseObj.title }}</h1>
          <h4 class="mb-1 d-inline">{{ courseName }}</h4>
          &nbsp;
          <div class="d-inline">
            <course-sections-open-badge :course="courseObj" />``
          </div>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <h6 class="mb-1 d-inline">{{ getCredits }} Credits</h6>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <p v-html="transformed" />
        </b-col>
      </b-row>
      <b-row>
        <b-col class="mb-4">
          <br />
          {{ courseObj.description }}
        </b-col>
      </b-row>
      <b-row class="mt-3">
        <b-col class="d-flex">
          <!-- Back Button -->
          <b-button variant="secondary" @click="$router.go(-1)">Back</b-button>
          
          <!-- Add/Remove Course Button -->
          <b-button 
            variant="secondary" 
            @click="toggleCourse(courseObj)"
            class="ml-2" 
            :style="courseObj.selected ? removeButtonStyle : addButtonStyle"
          >
            {{ courseObj.selected ? "Remove" : "Add" }}
          </b-button>
        </b-col>
      </b-row>
    </div>
    <CenterSpinner
      v-else-if="isLoadingCourses"
      :height="80"
      :fontSize="1.4"
      loadingMessage="Course"
      :topSpacing="30"
    />
    <!-- If !courseObj -->
    <div v-else class="w-90 ml-4 mb-4">
      <b-row>
        <b-col>
          <h1 class="mt-4">Course not found</h1>
          <p>
            This course may not exist, not offered this semester, or offered
            under a different name.
          </p>
          <b-button @click="$router.go(-1)">Back</b-button>
        </b-col>
      </b-row>
    </div>
  </b-container>
</template>

<script>
import { mapGetters, mapState } from "vuex";
import { COURSES } from "@/store";
import { generateRequirementsText } from "@/utils";
import CenterSpinnerComponent from "../components/CenterSpinner.vue";
import CourseSectionsOpenBadge from "../components/CourseSectionsOpenBadge.vue";

import { SelectedCoursesCookie } from "../controllers/SelectedCoursesCookie";
import {
  addStudentCourse,
  getStudentCourses,
  removeStudentCourse,
} from "@/services/YacsService";

export default {
  components: {
    CenterSpinner: CenterSpinnerComponent,
    CourseSectionsOpenBadge,
  },
  name: "CoursePage",
  data() {
    return {
      courseName: this.$route.params.course,
      selectedCourse: this.$route.params.courseObj,
      selectedCourses: {},
      breadcrumbNav: [
        {
          text: "YACS",
          to: "/",
        },
        {
          text: "Explore",
          to: "/explore",
        },
        {
          text: this.$route.params.subject,
          to: "/explore/" + this.$route.params.subject,
        },
        {
          text: this.$route.params.course,
        },
      ],
    };
  },
  methods: {
    generateRequirementsText,
    addCourse(course) {
      this.$set(this.selectedCourses, course.id, course);
      course.selected = true;
      if (this.isLoggedIn) {
        addStudentCourse({
          name: course.name,
          semester: this.selectedSemester,
          cid: "-1",
        });
      } else {
        SelectedCoursesCookie.load(this.$cookies)
          .semester(this.selectedSemester)
          .addCourse(course)
          .save();
      }
      course.sections.forEach((section) =>
        this.addCourseSection(course, section)
      );
    },
    addCourseSection(course, section) {
      section.selected = true;
      if (this.isLoggedIn) {
        addStudentCourse({
          name: course.name,
          semester: this.selectedSemester,
          cid: section.crn,
        });
      } else {
        SelectedCoursesCookie.load(this.$cookies)
          .semester(this.selectedSemester)
          .addCourseSection(course, section)
          .save();
      }
    },
    removeCourse(course) {
      this.$delete(this.selectedCourses, course.id);
      course.selected = false;

      course.sections.forEach((section) => this.removeCourseSection(section));

      if (this.isLoggedIn) {
        removeStudentCourse({
          name: course.name,
          semester: this.selectedSemester,
          cid: null,
        });
      } else {
        SelectedCoursesCookie.load(this.$cookies)
          .semester(this.selectedSemester)
          .removeCourse(course)
          .save();
      }
    },
    removeCourseSection(section) {
      if (section.selected) {
        section.selected = false;

        if (this.isLoggedIn) {
          removeStudentCourse({
            name: section.department + "-" + section.level,
            semester: this.selectedSemester,
            cid: section.crn,
          });
        } else {
          SelectedCoursesCookie.load(this.$cookies)
            .semester(this.selectedSemester)
            .removeCourseSection(section)
            .save();
        }
      }
    },
    toggleCourse(course) {
      if (course.selected) {
        this.removeCourse(course);
      } else {
        this.addCourse(course);
      }
    },
    async loadSelectedCourses() {
      if (this.isLoggedIn) {
        const cids = await getStudentCourses();
        cids.forEach((cid) => {
          if (cid.semester === this.selectedSemester) {
            const course = this.courses.find(
              (course) => course.name === cid.course_name
            );
            if (course) {
              this.$set(this.selectedCourses, course.id, course);
              course.selected = true;
            }
          }
        });
      } else {
        const selectedCoursesCookie = SelectedCoursesCookie.load(this.$cookies);
        try {
          selectedCoursesCookie
            .semester(this.selectedSemester)
            .selectedCourses.forEach((selectedCourse) => {
              const course = this.courses.find(
                (course) => course.id === selectedCourse.id
              );
              if (course) {
                this.$set(this.selectedCourses, course.id, course);
                course.selected = true;
              }
            });
        } catch (err) {
          selectedCoursesCookie.clear().save();
        }
      }
    },
  },
  computed: {
    ...mapState(["isLoadingCourses"]),
    ...mapGetters([COURSES]),
    isLoggedIn() {
      return this.$store.getters.isLoggedIn;
    },
    selectedSemester() {
      return this.$store.state.selectedSemester;
    },
    transformed() {
      let precoreqtext = this.courseObj.raw_precoreqs;
      if (precoreqtext === null) {
        return "No information on pre/corequisites";
      }
      const regex = /([A-Z]){4}( )([0-9]){4}/g;
      while (precoreqtext.search(regex) != -1) {
        let index = precoreqtext.search(regex);
        let beforetext = precoreqtext.slice(0, index);
        let dept = precoreqtext.slice(index, index + 4);
        let course_name = precoreqtext
          .slice(index, index + 9)
          .split(" ")
          .join("-");
        let link = '<a href="/explore/'.concat(
          dept,
          "/",
          course_name,
          '">',
          course_name,
          "</a>"
        );
        let aftertext = precoreqtext.slice(index + 9);
        precoreqtext = beforetext.concat(link, aftertext);
      }
      return precoreqtext;
    },
    courseObj() {
      const course = this.courses.find((course) => course.name === this.courseName);
      if (course) {
        course.selected = !!this.selectedCourses[course.id];
      }
      return course;
    },
    getCredits() {
      var credits;
      if (this.courseObj.min_credits != this.courseObj.max_credits) {
        credits = [this.courseObj.min_credits, this.courseObj.max_credits].join(
          "-"
        );
      } else {
        credits = this.courseObj.min_credits;
      }
      return credits;
    },
    // Styles for the Add button
    addButtonStyle() {
      return {
        backgroundColor: "#28a745",
        color: "white",
        border: "none",
        transition: "background-color 0.3s, border-color 0.3s",
      };
    },
    // Styles for the Remove button
    removeButtonStyle() {
      return {
        backgroundColor: "#dc3545",
        color: "white",
        border: "none",
        transition: "background-color 0.3s, border-color 0.3s",
      };
    },
  },
  mounted() {
    this.loadSelectedCourses();
  },
};
</script>