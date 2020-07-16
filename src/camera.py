import cv2


class Camera:
    # Use this function to edit the frame in the camera loop. Must return an np array of the same shape as frame
    # if you override
    def _edit_frame(self, frame):
        return frame

    def run_camera(self):
        cap = cv2.VideoCapture(0)

        # The loop to run the program
        is_running_correctly = cap.isOpened()
        while is_running_correctly:
            ret, frame = cap.read()
            if not ret:
                break

            # Edit the frame
            frame = self._edit_frame(frame)

            # Show the frame, and stop if the user clicks 'q'
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture and destroy the window after the user quits
        cap.release()
        cv2.destroyAllWindows()